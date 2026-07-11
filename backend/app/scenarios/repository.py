import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.persistence.models.agent import Agent, AgentProviderAccount
from app.persistence.models.area import Area
from app.persistence.models.audit import AuditEvent, MetricObservation
from app.persistence.models.balance import ProviderBalanceSnapshot, SharedCashSnapshot
from app.persistence.models.enums import (
    AccountStatus,
    AgentStatus,
    ScenarioRunStatus,
    Severity,
    TransactionStatus,
)
from app.persistence.models.feed import DataQualityEvent, ProviderFeedStatus
from app.persistence.models.provider import Provider
from app.persistence.models.scenario import Scenario, ScenarioRun
from app.persistence.models.transaction import Transaction
from app.scenarios.catalog import CANONICAL_SCENARIOS, PROVIDERS
from app.scenarios.exceptions import DuplicateScenarioRunError, ScenarioNotFoundError
from app.scenarios.random_source import validate_synthetic_identifier
from app.scenarios.schemas import (
    CATALOG_VERSION,
    GENERATOR_VERSION,
    GeneratedScenario,
    ScenarioConfig,
)


@dataclass(frozen=True)
class ReferenceData:
    scenario: Scenario
    agent: Agent
    providers_by_code: dict[str, Provider]
    accounts_by_provider_code: dict[str, AgentProviderAccount]


class ScenarioRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_catalog(self) -> tuple[Scenario, ...]:
        self.ensure_reference_data()
        return tuple(self.session.scalars(select(Scenario).order_by(Scenario.code)).all())

    def next_run_ref(self) -> str:
        count = self.session.scalar(select(func.count()).select_from(ScenarioRun)) or 0
        return validate_synthetic_identifier(f"SIM-RUN-{count + 1:06d}")

    def assert_run_ref_available(self, run_ref: str) -> None:
        existing = self.session.scalar(
            select(AuditEvent.id).where(
                AuditEvent.action == "scenario.run_created",
                AuditEvent.correlation_id == run_ref,
            )
        )
        if existing is not None:
            raise DuplicateScenarioRunError(f"scenario run already exists: {run_ref}")

    def ensure_reference_data(self) -> None:
        area = self.session.scalar(select(Area).where(Area.code == "SIM-AREA-001"))
        if area is None:
            area = Area(code="SIM-AREA-001", display_name="Demo Area")
            self.session.add(area)
            self.session.flush()

        agent = self.session.scalar(
            select(Agent).where(Agent.synthetic_agent_ref == "SIM-AGENT-0001")
        )
        if agent is None:
            agent = Agent(
                area_id=area.id,
                synthetic_agent_ref=validate_synthetic_identifier("SIM-AGENT-0001"),
                display_code="Demo Outlet 001",
                status=AgentStatus.ACTIVE,
            )
            self.session.add(agent)
            self.session.flush()

        for definition in CANONICAL_SCENARIOS.values():
            scenario = self.session.scalar(select(Scenario).where(Scenario.code == definition.code))
            if scenario is None:
                self.session.add(
                    Scenario(
                        code=definition.code,
                        name=definition.name,
                        description=definition.purpose,
                    )
                )

        for short_code, display_name, synthetic_ref in PROVIDERS:
            provider = self.session.scalar(select(Provider).where(Provider.code == synthetic_ref))
            if provider is None:
                provider = Provider(
                    code=synthetic_ref,
                    display_name=display_name,
                    boundary_note=(
                        "Synthetic provider context; no production affiliation or balance merging."
                    ),
                )
                self.session.add(provider)
                self.session.flush()
            account_ref = validate_synthetic_identifier(f"SIM-ACCT-{short_code}-0001")
            account = self.session.scalar(
                select(AgentProviderAccount).where(
                    AgentProviderAccount.agent_id == agent.id,
                    AgentProviderAccount.provider_id == provider.id,
                )
            )
            if account is None:
                self.session.add(
                    AgentProviderAccount(
                        agent_id=agent.id,
                        provider_id=provider.id,
                        synthetic_account_ref=account_ref,
                        status=AccountStatus.ACTIVE,
                    )
                )
        self.session.flush()

    def reference_data_for(self, scenario_code: str) -> ReferenceData:
        self.ensure_reference_data()
        scenario = self.session.scalar(select(Scenario).where(Scenario.code == scenario_code))
        if scenario is None:
            raise ScenarioNotFoundError(scenario_code)
        agent = self.session.scalar(
            select(Agent).where(Agent.synthetic_agent_ref == "SIM-AGENT-0001")
        )
        if agent is None:
            raise ScenarioNotFoundError("SIM-AGENT-0001")

        providers_by_code: dict[str, Provider] = {}
        accounts_by_provider_code: dict[str, AgentProviderAccount] = {}
        for short_code, _display_name, synthetic_ref in PROVIDERS:
            provider = self.session.scalar(select(Provider).where(Provider.code == synthetic_ref))
            if provider is None:
                raise ScenarioNotFoundError(synthetic_ref)
            account = self.session.scalar(
                select(AgentProviderAccount).where(
                    AgentProviderAccount.agent_id == agent.id,
                    AgentProviderAccount.provider_id == provider.id,
                )
            )
            if account is None:
                raise ScenarioNotFoundError(f"SIM-ACCT-{short_code}-0001")
            providers_by_code[short_code] = provider
            accounts_by_provider_code[short_code] = account
        return ReferenceData(scenario, agent, providers_by_code, accounts_by_provider_code)

    def create_run(
        self,
        generated: GeneratedScenario,
        refs: ReferenceData,
        config: ScenarioConfig,
    ) -> ScenarioRun:
        run = ScenarioRun(
            scenario_id=refs.scenario.id,
            seed=generated.seed,
            status=ScenarioRunStatus.RUNNING,
            started_at=generated.start_timestamp,
        )
        self.session.add(run)
        self.session.flush()
        self._persist_run_created_audit(run, generated, config)
        self.persist_generated_records(run, generated, refs)
        return run

    def persist_generated_records(
        self,
        run: ScenarioRun,
        generated: GeneratedScenario,
        refs: ReferenceData,
    ) -> None:
        refs.agent.status = (
            AgentStatus.ACTIVE if generated.agent_available else AgentStatus.INACTIVE
        )
        for snapshot in generated.shared_cash:
            self.session.add(
                SharedCashSnapshot(
                    agent_id=refs.agent.id,
                    amount=snapshot.amount,
                    currency=snapshot.currency,
                    observed_at=snapshot.observed_at,
                    scenario_run_id=run.id,
                )
            )

        for snapshot in generated.provider_balances:
            if snapshot.provider_code is None:
                continue
            provider = refs.providers_by_code[snapshot.provider_code]
            account = refs.accounts_by_provider_code[snapshot.provider_code]
            self.session.add(
                ProviderBalanceSnapshot(
                    account_id=account.id,
                    agent_id=refs.agent.id,
                    provider_id=provider.id,
                    amount=snapshot.amount,
                    currency=snapshot.currency,
                    observed_at=snapshot.observed_at,
                    quality_status=snapshot.quality_status,
                    scenario_run_id=run.id,
                )
            )

        for tx in generated.transactions:
            provider = refs.providers_by_code[tx.provider_code]
            account = refs.accounts_by_provider_code[tx.provider_code]
            self.session.add(
                Transaction(
                    account_id=account.id,
                    agent_id=refs.agent.id,
                    provider_id=provider.id,
                    synthetic_transaction_ref=tx.synthetic_transaction_ref,
                    synthetic_account_ref=tx.synthetic_account_ref,
                    synthetic_customer_ref=tx.synthetic_customer_ref,
                    transaction_type=tx.transaction_type,
                    amount=tx.amount,
                    currency=tx.currency,
                    status=TransactionStatus.COMPLETED,
                    occurred_at=tx.occurred_at,
                    scenario_run_id=run.id,
                )
            )

        self.session.flush()
        for feed in generated.feed_statuses:
            provider = refs.providers_by_code[feed.provider_code]
            feed_row = ProviderFeedStatus(
                provider_id=provider.id,
                agent_id=refs.agent.id,
                scenario_run_id=run.id,
                status=feed.status,
                observed_at=feed.observed_at,
                ingested_at=feed.ingested_at,
            )
            self.session.add(feed_row)
            self.session.flush()
            if feed.event_type is not None:
                self.session.add(
                    DataQualityEvent(
                        feed_status_id=feed_row.id,
                        event_type=feed.event_type,
                        severity=Severity.MEDIUM,
                        details={
                            "scenario_run_ref": generated.run_ref,
                            "source": "synthetic_scenario_engine",
                        },
                    )
                )

        for event in generated.ground_truth:
            self.session.add(
                AuditEvent(
                    provider_id=refs.providers_by_code[event.provider_scope].id
                    if event.provider_scope in refs.providers_by_code
                    else None,
                    action="scenario.ground_truth_event",
                    entity_type="scenario_run",
                    entity_id=run.id,
                    correlation_id=generated.run_ref,
                    metadata_json={
                        "category": event.category,
                        "agent_scope": event.agent_scope,
                        "provider_scope": event.provider_scope,
                        "start_time": event.start_time.isoformat(),
                        "end_time": event.end_time.isoformat(),
                        "affected_transaction_refs": list(event.affected_transaction_refs),
                        "expected_review_boundary": event.expected_review_boundary,
                        "anomaly_positive": event.anomaly_positive,
                        "false_positive_case": event.false_positive_case,
                    },
                )
            )
        run.status = ScenarioRunStatus.COMPLETED
        run.ended_at = generated.start_timestamp + timedelta(hours=2)
        self.session.add(
            AuditEvent(
                action="scenario.run_completed",
                entity_type="scenario_run",
                entity_id=run.id,
                correlation_id=generated.run_ref,
                metadata_json=self.completed_metadata(generated),
            )
        )
        self.session.flush()

    def completed_metadata(self, generated: GeneratedScenario) -> dict[str, Any]:
        return {
            "run_ref": generated.run_ref,
            "scenario_code": generated.definition.code,
            "scenario_version": generated.definition.version,
            "catalog_version": CATALOG_VERSION,
            "generator_version": GENERATOR_VERSION,
            "seed": generated.seed,
            "profile": generated.profile,
            "start_timestamp": generated.start_timestamp.isoformat(),
            "generated_counts": generated.generated_counts,
            "dataset_fingerprint": generated.fingerprint,
            "ground_truth_summary": [
                {
                    "category": event.category,
                    "anomaly_positive": event.anomaly_positive,
                    "false_positive_case": event.false_positive_case,
                }
                for event in generated.ground_truth
            ],
        }

    def _persist_run_created_audit(
        self,
        run: ScenarioRun,
        generated: GeneratedScenario,
        config: ScenarioConfig,
    ) -> None:
        self.session.add(
            AuditEvent(
                action="scenario.run_created",
                entity_type="scenario_run",
                entity_id=run.id,
                correlation_id=generated.run_ref,
                metadata_json={
                    "run_ref": generated.run_ref,
                    "scenario_code": generated.definition.code,
                    "scenario_version": generated.definition.version,
                    "catalog_version": CATALOG_VERSION,
                    "generator_version": GENERATOR_VERSION,
                    "seed": generated.seed,
                    "profile": generated.profile,
                    "start_timestamp": generated.start_timestamp.isoformat(),
                    "generation_config": {
                        "profile": config.profile,
                        "explicit_start_timestamp": config.start_timestamp is not None,
                    },
                },
            )
        )

    def find_run(self, run_ref_or_uuid: str) -> ScenarioRun:
        run_id = _parse_uuid(run_ref_or_uuid)
        if run_id is not None:
            run = self.session.get(ScenarioRun, run_id)
        else:
            audit = self.session.scalar(
                select(AuditEvent).where(
                    AuditEvent.action == "scenario.run_created",
                    AuditEvent.correlation_id == run_ref_or_uuid,
                )
            )
            run = self.session.get(ScenarioRun, audit.entity_id) if audit is not None else None
        if run is None:
            raise ScenarioNotFoundError(run_ref_or_uuid)
        return run

    def run_created_metadata(self, run: ScenarioRun) -> dict[str, Any]:
        audit = self.session.scalar(
            select(AuditEvent).where(
                AuditEvent.action == "scenario.run_created",
                AuditEvent.entity_id == run.id,
            )
        )
        if audit is None:
            raise ScenarioNotFoundError(f"missing run metadata for {run.id}")
        return audit.metadata_json

    def latest_completed_metadata(self, run: ScenarioRun) -> dict[str, Any] | None:
        audit = self.session.scalar(
            select(AuditEvent)
            .where(
                AuditEvent.action == "scenario.run_completed",
                AuditEvent.entity_id == run.id,
            )
            .order_by(AuditEvent.created_at.desc())
        )
        return None if audit is None else audit.metadata_json

    def reset_run_data(self, run: ScenarioRun) -> None:
        feed_ids = select(ProviderFeedStatus.id).where(ProviderFeedStatus.scenario_run_id == run.id)
        self.session.execute(
            delete(DataQualityEvent).where(DataQualityEvent.feed_status_id.in_(feed_ids))
        )
        self.session.execute(delete(Transaction).where(Transaction.scenario_run_id == run.id))
        self.session.execute(
            delete(ProviderBalanceSnapshot).where(ProviderBalanceSnapshot.scenario_run_id == run.id)
        )
        self.session.execute(
            delete(SharedCashSnapshot).where(SharedCashSnapshot.scenario_run_id == run.id)
        )
        self.session.execute(
            delete(ProviderFeedStatus).where(ProviderFeedStatus.scenario_run_id == run.id)
        )
        self.session.execute(
            delete(MetricObservation).where(MetricObservation.scenario_run_id == run.id)
        )
        self.session.execute(
            delete(AuditEvent).where(
                AuditEvent.entity_id == run.id,
                AuditEvent.action.in_(
                    [
                        "scenario.ground_truth_event",
                        "scenario.run_completed",
                        "scenario.run_reset",
                    ]
                ),
            )
        )
        run.status = ScenarioRunStatus.PENDING
        run.ended_at = None
        self.session.add(
            AuditEvent(
                action="scenario.run_reset",
                entity_type="scenario_run",
                entity_id=run.id,
                correlation_id=self.run_created_metadata(run)["run_ref"],
                metadata_json={
                    "reset_at": datetime.now(UTC).isoformat(),
                    "scope": "selected_run_only",
                },
            )
        )


def _parse_uuid(value: str) -> uuid.UUID | None:
    try:
        return uuid.UUID(value)
    except ValueError:
        return None
