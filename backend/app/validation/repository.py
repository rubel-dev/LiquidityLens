import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.agent import Agent, AgentProviderAccount
from app.persistence.models.audit import AuditEvent
from app.persistence.models.balance import ProviderBalanceSnapshot, SharedCashSnapshot
from app.persistence.models.enums import FeedQualityStatus, Severity, TransactionStatus
from app.persistence.models.feed import DataQualityEvent, ProviderFeedStatus
from app.persistence.models.provider import Provider
from app.persistence.models.scenario import ScenarioRun
from app.persistence.models.transaction import Transaction
from app.validation.audit import validation_audit_event
from app.validation.enums import ValidationSeverity
from app.validation.schemas import (
    CanonicalFeedStatusInput,
    CanonicalProviderBalanceInput,
    CanonicalSharedCashInput,
    CanonicalTransactionInput,
    ValidationFinding,
)


class ValidationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def provider_by_code(self, provider_code: str) -> Provider | None:
        return self.session.scalar(select(Provider).where(Provider.code == provider_code))

    def agent_by_ref(self, agent_ref: str) -> Agent | None:
        return self.session.scalar(select(Agent).where(Agent.synthetic_agent_ref == agent_ref))

    def account_by_ref(self, account_ref: str) -> AgentProviderAccount | None:
        return self.session.scalar(
            select(AgentProviderAccount).where(
                AgentProviderAccount.synthetic_account_ref == account_ref,
            )
        )

    def scenario_run_by_ref(self, run_ref: str | None) -> ScenarioRun | None:
        if run_ref is None:
            return None
        audit = self.session.scalar(
            select(AuditEvent).where(
                AuditEvent.action == "scenario.run_created",
                AuditEvent.correlation_id == run_ref,
            )
        )
        return None if audit is None else self.session.get(ScenarioRun, audit.entity_id)

    def transaction_by_ref(self, transaction_ref: str) -> Transaction | None:
        return self.session.scalar(
            select(Transaction).where(
                Transaction.synthetic_transaction_ref == transaction_ref,
            )
        )

    def provider_balance_duplicate(
        self,
        record: CanonicalProviderBalanceInput,
        account: AgentProviderAccount,
    ) -> ProviderBalanceSnapshot | None:
        return self.session.scalar(
            select(ProviderBalanceSnapshot).where(
                ProviderBalanceSnapshot.account_id == account.id,
                ProviderBalanceSnapshot.observed_at == record.balance_timestamp,
            )
        )

    def shared_cash_duplicate(
        self,
        record: CanonicalSharedCashInput,
        agent: Agent,
    ) -> SharedCashSnapshot | None:
        return self.session.scalar(
            select(SharedCashSnapshot).where(
                SharedCashSnapshot.agent_id == agent.id,
                SharedCashSnapshot.observed_at == record.snapshot_timestamp,
            )
        )

    def latest_provider_balance(
        self,
        account: AgentProviderAccount,
    ) -> ProviderBalanceSnapshot | None:
        return self.session.scalar(
            select(ProviderBalanceSnapshot)
            .where(ProviderBalanceSnapshot.account_id == account.id)
            .order_by(ProviderBalanceSnapshot.observed_at.desc())
        )

    def latest_transaction(self, account: AgentProviderAccount) -> Transaction | None:
        return self.session.scalar(
            select(Transaction)
            .where(Transaction.account_id == account.id)
            .order_by(Transaction.occurred_at.desc())
        )

    def latest_transaction_source_sequence(
        self,
        provider: Provider,
        account_ref: str,
    ) -> int | None:
        audits = self.session.scalars(
            select(AuditEvent)
            .where(
                AuditEvent.provider_id == provider.id,
                AuditEvent.entity_type == "transaction",
                AuditEvent.action.in_(
                    ("validation.record_accepted", "validation.warning_generated")
                ),
            )
            .order_by(AuditEvent.created_at.desc())
            .limit(50)
        )
        for audit in audits:
            metadata = audit.metadata_json
            if metadata.get("account_ref") != account_ref:
                continue
            sequence = metadata.get("source_sequence")
            if isinstance(sequence, int):
                return sequence
        return None

    def persist_transaction(
        self,
        record: CanonicalTransactionInput,
        provider: Provider,
        agent: Agent,
        account: AgentProviderAccount,
        scenario_run: ScenarioRun | None,
    ) -> Transaction:
        transaction = Transaction(
            account_id=account.id,
            agent_id=agent.id,
            provider_id=provider.id,
            synthetic_transaction_ref=record.synthetic_transaction_ref,
            synthetic_account_ref=record.synthetic_account_ref,
            synthetic_customer_ref=record.synthetic_customer_ref,
            transaction_type=record.transaction_type,
            amount=record.amount,
            currency=record.currency,
            status=record.source_status
            if isinstance(record.source_status, TransactionStatus)
            else TransactionStatus(str(record.source_status)),
            occurred_at=record.event_timestamp,
            scenario_run_id=None if scenario_run is None else scenario_run.id,
        )
        self.session.add(transaction)
        self.session.flush()
        return transaction

    def persist_provider_balance(
        self,
        record: CanonicalProviderBalanceInput,
        provider: Provider,
        agent: Agent,
        account: AgentProviderAccount,
        scenario_run: ScenarioRun | None,
        quality_status: str,
    ) -> ProviderBalanceSnapshot:
        snapshot = ProviderBalanceSnapshot(
            account_id=account.id,
            agent_id=agent.id,
            provider_id=provider.id,
            amount=record.reported_balance,
            currency="BDT",
            observed_at=record.balance_timestamp,
            quality_status=quality_status,
            scenario_run_id=None if scenario_run is None else scenario_run.id,
        )
        self.session.add(snapshot)
        self.session.flush()
        return snapshot

    def persist_shared_cash(
        self,
        record: CanonicalSharedCashInput,
        agent: Agent,
        scenario_run: ScenarioRun | None,
    ) -> SharedCashSnapshot:
        snapshot = SharedCashSnapshot(
            agent_id=agent.id,
            amount=record.reported_cash,
            currency="BDT",
            observed_at=record.snapshot_timestamp,
            scenario_run_id=None if scenario_run is None else scenario_run.id,
        )
        self.session.add(snapshot)
        self.session.flush()
        return snapshot

    def persist_feed_status(
        self,
        record: CanonicalFeedStatusInput,
        provider: Provider,
        agent: Agent | None,
        scenario_run: ScenarioRun | None,
        status: FeedQualityStatus,
    ) -> ProviderFeedStatus:
        feed = ProviderFeedStatus(
            provider_id=provider.id,
            agent_id=None if agent is None else agent.id,
            scenario_run_id=None if scenario_run is None else scenario_run.id,
            status=status,
            observed_at=record.expected_timestamp,
            ingested_at=record.received_timestamp,
        )
        self.session.add(feed)
        self.session.flush()
        return feed

    def persist_quality_events(
        self,
        feed_status: ProviderFeedStatus,
        findings: tuple[ValidationFinding, ...],
    ) -> None:
        existing_types = {
            event.event_type
            for event in self.session.scalars(
                select(DataQualityEvent).where(DataQualityEvent.feed_status_id == feed_status.id)
            )
        }
        for finding in findings:
            if finding.category.value in existing_types:
                continue
            self.session.add(
                DataQualityEvent(
                    feed_status_id=feed_status.id,
                    event_type=finding.category.value,
                    severity=_severity_for(finding.severity),
                    details={
                        "finding_id": finding.finding_id,
                        "rule_id": finding.rule_id,
                        "fields": list(finding.fields),
                        "expected": finding.expected,
                        "observed": finding.observed,
                        "evidence": finding.evidence,
                        "safe_next_step": finding.safe_next_step,
                        "usability": finding.usability.value,
                    },
                )
            )

    def persist_audit(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: uuid.UUID | None,
        provider: Provider | None,
        correlation_id: str | None,
        findings: tuple[ValidationFinding, ...],
        metadata: dict[str, object] | None = None,
    ) -> None:
        self.session.add(
            validation_audit_event(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id or uuid.uuid4(),
                provider=provider,
                correlation_id=correlation_id,
                findings=findings,
                metadata=metadata,
            )
        )

    def synthetic_validation_feed(
        self,
        provider: Provider,
        agent: Agent | None,
        scenario_run: ScenarioRun | None,
        status: FeedQualityStatus = FeedQualityStatus.INVALID,
    ) -> ProviderFeedStatus:
        feed = ProviderFeedStatus(
            provider_id=provider.id,
            agent_id=None if agent is None else agent.id,
            scenario_run_id=None if scenario_run is None else scenario_run.id,
            status=status,
            observed_at=datetime.now(UTC),
            ingested_at=datetime.now(UTC),
        )
        self.session.add(feed)
        self.session.flush()
        return feed


def _severity_for(severity: ValidationSeverity) -> Severity:
    if severity == ValidationSeverity.HIGH:
        return Severity.HIGH
    if severity == ValidationSeverity.MEDIUM:
        return Severity.MEDIUM
    return Severity.LOW
