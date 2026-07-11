import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.anomaly.exceptions import AnomalySubjectNotFoundError
from app.anomaly.schemas import (
    RULE_NAME,
    RULE_VERSION,
    AnomalyDataQuality,
    AnomalyFindingResult,
    AnomalyRuleConfig,
    AnomalyTransaction,
)
from app.persistence.models.agent import Agent, AgentProviderAccount
from app.persistence.models.analytics import (
    AnomalyFinding,
    ConfidenceAssessment,
    EvidenceItem,
    RuleVersion,
)
from app.persistence.models.enums import FeedQualityStatus, TransactionStatus, TransactionType
from app.persistence.models.feed import ProviderFeedStatus
from app.persistence.models.scenario import Scenario, ScenarioRun
from app.persistence.models.transaction import Transaction


class AnomalyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self._active_rule: RuleVersion | None = None

    def require_agent(self, agent_id: uuid.UUID) -> Agent:
        agent = self.session.get(Agent, agent_id)
        if agent is None:
            raise AnomalySubjectNotFoundError(f"agent not found: {agent_id}")
        return agent

    def require_run(self, scenario_run_id: uuid.UUID | None) -> ScenarioRun | None:
        if scenario_run_id is None:
            return None
        run = self.session.get(ScenarioRun, scenario_run_id)
        if run is None:
            raise AnomalySubjectNotFoundError(f"scenario run not found: {scenario_run_id}")
        return run

    def provider_ids_for_agent(self, agent_id: uuid.UUID) -> tuple[uuid.UUID, ...]:
        return tuple(
            self.session.scalars(
                select(AgentProviderAccount.provider_id)
                .where(AgentProviderAccount.agent_id == agent_id)
                .order_by(AgentProviderAccount.provider_id)
            ).all()
        )

    def cash_out_transactions(
        self,
        agent_id: uuid.UUID,
        provider_id: uuid.UUID,
        scenario_run_id: uuid.UUID | None,
        detected_at: datetime,
        config: AnomalyRuleConfig,
    ) -> tuple[AnomalyTransaction, ...]:
        start = detected_at - timedelta(
            days=config.baseline_window_days,
            minutes=config.rolling_window_minutes,
        )
        query = select(Transaction).where(
            Transaction.agent_id == agent_id,
            Transaction.provider_id == provider_id,
            Transaction.transaction_type == TransactionType.CASH_OUT,
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.occurred_at >= start,
            Transaction.occurred_at <= detected_at,
        )
        if scenario_run_id is not None:
            query = query.where(Transaction.scenario_run_id == scenario_run_id)
        rows = self.session.scalars(query.order_by(Transaction.occurred_at)).all()
        return tuple(
            AnomalyTransaction(
                transaction_id=row.id,
                provider_id=row.provider_id,
                agent_id=row.agent_id,
                synthetic_customer_ref=row.synthetic_customer_ref,
                amount=Decimal(row.amount),
                occurred_at=row.occurred_at,
            )
            for row in rows
        )

    def data_quality(
        self,
        agent_id: uuid.UUID,
        provider_id: uuid.UUID,
        scenario_run_id: uuid.UUID | None,
    ) -> AnomalyDataQuality:
        query = select(ProviderFeedStatus).where(
            ProviderFeedStatus.agent_id == agent_id,
            ProviderFeedStatus.provider_id == provider_id,
        )
        if scenario_run_id is not None:
            query = query.where(ProviderFeedStatus.scenario_run_id == scenario_run_id)
        feed = self.session.scalar(query.order_by(ProviderFeedStatus.observed_at.desc()))
        status = FeedQualityStatus.MISSING if feed is None else feed.status
        multiplier = {
            FeedQualityStatus.COMPLETE: Decimal("1.00"),
            FeedQualityStatus.DELAYED: Decimal("0.80"),
            FeedQualityStatus.STALE: Decimal("0.80"),
            FeedQualityStatus.MISSING: Decimal("0.60"),
            FeedQualityStatus.CONFLICTING: Decimal("0.70"),
            FeedQualityStatus.INVALID: Decimal("0.50"),
        }[status]
        complete = status not in {
            FeedQualityStatus.MISSING,
            FeedQualityStatus.CONFLICTING,
            FeedQualityStatus.INVALID,
        }
        issues = () if status == FeedQualityStatus.COMPLETE else (f"{status.value} provider feed",)
        return AnomalyDataQuality(
            multiplier=multiplier,
            complete=complete,
            statuses=(status,),
            issues=issues,
        )

    def event_context(self, run: ScenarioRun | None) -> str:
        if run is None:
            return "standard"
        scenario = self.session.get(Scenario, run.scenario_id)
        if scenario is None:
            return "standard"
        if scenario.code == "eid_rush":
            return "eid"
        if scenario.code == "salary_day_legitimate_spike":
            return "salary_day"
        return "standard"

    def persist(
        self,
        result: AnomalyFindingResult,
        config: AnomalyRuleConfig,
    ) -> uuid.UUID:
        rule = self._rule_version(config)
        finding_id = uuid.uuid4()
        finding = AnomalyFinding(
            id=finding_id,
            provider_id=result.provider_id,
            agent_id=result.agent_id,
            rule_version_id=rule.id,
            finding_type=result.pattern,
            severity=result.severity.value,
            score=result.score,
            detected_at=result.detected_at,
            human_review_required=result.requires_review,
        )
        self.session.add(finding)
        self.session.flush([finding])
        for item in result.evidence:
            self.session.add(
                EvidenceItem(
                    finding_id=finding_id,
                    evidence_type=item.evidence_type,
                    payload={
                        "label": item.label,
                        "value": item.value,
                        "weight": str(item.weight),
                        "detail": item.detail,
                    },
                )
            )
        self.session.add(
            ConfidenceAssessment(
                subject_type="anomaly_finding",
                subject_id=finding_id,
                confidence=result.confidence,
                reasons={
                    "tier": result.confidence_tier,
                    "uncertainty": list(result.uncertainty),
                    "requires_review": result.requires_review,
                    "recommendation": result.recommendation,
                    "rule_version_id": str(rule.id),
                },
            )
        )
        return finding_id

    def _rule_version(self, config: AnomalyRuleConfig) -> RuleVersion:
        if self._active_rule is not None:
            return self._active_rule
        rule = self.session.scalar(
            select(RuleVersion).where(
                RuleVersion.name == RULE_NAME,
                RuleVersion.version == RULE_VERSION,
            )
        )
        if rule is None:
            rule = RuleVersion(
                id=uuid.uuid4(),
                name=RULE_NAME,
                version=RULE_VERSION,
                config={
                    "amount_similarity_pct": str(config.amount_similarity_pct),
                    "rolling_window_minutes": config.rolling_window_minutes,
                    "velocity_multiplier": str(config.velocity_multiplier),
                    "minimum_cash_out_count": config.minimum_cash_out_count,
                    "maximum_synthetic_group_size": config.maximum_synthetic_group_size,
                    "baseline_window_days": config.baseline_window_days,
                    "minimum_confidence_to_review": str(config.minimum_confidence_to_review),
                    "review_severity_threshold": config.review_severity_threshold.value,
                },
                active=True,
            )
            self.session.add(rule)
            self.session.flush([rule])
        self._active_rule = rule
        return rule
