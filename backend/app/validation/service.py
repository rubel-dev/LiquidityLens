from dataclasses import replace

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.persistence.models.agent import Agent
from app.persistence.models.enums import FeedQualityStatus
from app.persistence.models.provider import Provider
from app.persistence.models.scenario import ScenarioRun
from app.providers.base import CanonicalRecord
from app.providers.schemas import SimulatedProviderRecord
from app.providers.simulated import SimulatedProviderAdapter
from app.validation.balance_validator import (
    validate_provider_balance_input,
    validate_shared_cash_input,
)
from app.validation.enums import RecordDisposition, RecordUsability
from app.validation.feed_validator import status_for_findings, validate_feed_status_input
from app.validation.normalizer import (
    canonical_feed_status,
    canonical_provider_balance,
    canonical_shared_cash,
    canonical_transaction,
)
from app.validation.quality_score import disposition_for, score_findings
from app.validation.repository import ValidationRepository
from app.validation.schemas import (
    CanonicalFeedStatusInput,
    CanonicalProviderBalanceInput,
    CanonicalSharedCashInput,
    CanonicalTransactionInput,
    ValidationFinding,
    ValidationResult,
    ValidationSettings,
)
from app.validation.transaction_validator import validate_transaction_input


class ValidationService:
    def __init__(self, session: Session, settings: Settings | None = None) -> None:
        self.session = session
        self.repository = ValidationRepository(session)
        self.settings = validation_settings(settings or get_settings())

    def validate_transaction(self, record: CanonicalTransactionInput) -> ValidationResult:
        canonical = canonical_transaction(record)
        provider = self.repository.provider_by_code(canonical.provider_code)
        agent = self.repository.agent_by_ref(canonical.agent_ref)
        account = self.repository.account_by_ref(canonical.account_ref)
        duplicate = (
            self.repository.transaction_by_ref(canonical.synthetic_transaction_ref) is not None
        )
        latest = None if account is None else self.repository.latest_transaction(account)
        latest_sequence = (
            None
            if provider is None or account is None
            else self.repository.latest_transaction_source_sequence(
                provider,
                canonical.account_ref,
            )
        )
        findings = validate_transaction_input(
            canonical,
            self.settings,
            provider,
            agent,
            account,
            duplicate,
            None if latest is None else latest.occurred_at,
            latest_sequence,
        )
        return _result(canonical, findings)

    def ingest_transaction(self, record: CanonicalTransactionInput) -> ValidationResult:
        canonical = canonical_transaction(record)
        with self.session.begin():
            provider = self.repository.provider_by_code(canonical.provider_code)
            agent = self.repository.agent_by_ref(canonical.agent_ref)
            account = self.repository.account_by_ref(canonical.account_ref)
            duplicate_row = self.repository.transaction_by_ref(canonical.synthetic_transaction_ref)
            latest = None if account is None else self.repository.latest_transaction(account)
            latest_sequence = (
                None
                if provider is None or account is None
                else self.repository.latest_transaction_source_sequence(
                    provider,
                    canonical.account_ref,
                )
            )
            findings = validate_transaction_input(
                canonical,
                self.settings,
                provider,
                agent,
                account,
                duplicate_row is not None,
                None if latest is None else latest.occurred_at,
                latest_sequence,
            )
            result = _result(canonical, findings)
            scenario_run = self.repository.scenario_run_by_ref(canonical.scenario_run_ref)
            if result.disposition == RecordDisposition.DUPLICATE_IGNORED:
                self.repository.persist_audit(
                    action="validation.duplicate_ignored",
                    entity_type="transaction",
                    entity_id=None if duplicate_row is None else duplicate_row.id,
                    provider=provider,
                    correlation_id=canonical.synthetic_transaction_ref,
                    findings=findings,
                    metadata={"disposition": result.disposition.value},
                )
                persisted_id = None if duplicate_row is None else str(duplicate_row.id)
                return replace(result, persisted_id=persisted_id)
            if result.disposition == RecordDisposition.REJECTED:
                self._persist_rejection(
                    provider=provider,
                    agent=agent,
                    scenario_run=scenario_run,
                    findings=findings,
                    action="validation.record_rejected",
                    correlation_id=canonical.synthetic_transaction_ref,
                    entity_type="transaction",
                )
                return result
            assert provider is not None and agent is not None and account is not None
            persisted = self.repository.persist_transaction(
                canonical,
                provider,
                agent,
                account,
                scenario_run,
            )
            self._persist_warning_if_needed(provider, agent, scenario_run, findings)
            self.repository.persist_audit(
                action="validation.record_accepted"
                if result.disposition == RecordDisposition.ACCEPTED
                else "validation.warning_generated",
                entity_type="transaction",
                entity_id=persisted.id,
                provider=provider,
                correlation_id=canonical.synthetic_transaction_ref,
                findings=findings,
                metadata={
                    "disposition": result.disposition.value,
                    "quality_score": str(result.quality_score.overall_score),
                    "account_ref": canonical.account_ref,
                    "source_sequence": canonical.source_sequence,
                },
            )
            return replace(result, persisted_id=str(persisted.id))

    def ingest_provider_balance(self, record: CanonicalProviderBalanceInput) -> ValidationResult:
        canonical = canonical_provider_balance(record)
        with self.session.begin():
            provider = self.repository.provider_by_code(canonical.provider_code)
            agent = self.repository.agent_by_ref(canonical.agent_ref)
            account = self.repository.account_by_ref(canonical.account_ref)
            duplicate = (
                False
                if account is None
                else self.repository.provider_balance_duplicate(canonical, account) is not None
            )
            previous = None if account is None else self.repository.latest_provider_balance(account)
            findings = validate_provider_balance_input(
                canonical,
                self.settings,
                provider,
                agent,
                account,
                duplicate,
                previous,
            )
            result = _result(canonical, findings)
            scenario_run = self.repository.scenario_run_by_ref(canonical.scenario_run_ref)
            if result.disposition == RecordDisposition.REJECTED:
                self._persist_rejection(
                    provider,
                    agent,
                    scenario_run,
                    findings,
                    "validation.record_rejected",
                    canonical.account_ref,
                    "provider_balance",
                )
                return result
            if result.disposition == RecordDisposition.QUARANTINED:
                self._persist_rejection(
                    provider,
                    agent,
                    scenario_run,
                    findings,
                    "validation.record_quarantined",
                    canonical.account_ref,
                    "provider_balance",
                )
                return result
            assert provider is not None and agent is not None and account is not None
            persisted = self.repository.persist_provider_balance(
                canonical,
                provider,
                agent,
                account,
                scenario_run,
                "complete" if not findings else "warning",
            )
            self._persist_warning_if_needed(provider, agent, scenario_run, findings)
            self.repository.persist_audit(
                action="validation.record_accepted",
                entity_type="provider_balance",
                entity_id=persisted.id,
                provider=provider,
                correlation_id=canonical.account_ref,
                findings=findings,
                metadata={"disposition": result.disposition.value},
            )
            return replace(result, persisted_id=str(persisted.id))

    def ingest_shared_cash(self, record: CanonicalSharedCashInput) -> ValidationResult:
        canonical = canonical_shared_cash(record)
        with self.session.begin():
            agent = self.repository.agent_by_ref(canonical.agent_ref)
            duplicate = (
                False
                if agent is None
                else self.repository.shared_cash_duplicate(canonical, agent) is not None
            )
            findings = validate_shared_cash_input(canonical, self.settings, agent, duplicate)
            result = _result(canonical, findings)
            scenario_run = self.repository.scenario_run_by_ref(canonical.scenario_run_ref)
            if result.disposition == RecordDisposition.REJECTED:
                self._persist_rejection(
                    None,
                    agent,
                    scenario_run,
                    findings,
                    "validation.record_rejected",
                    canonical.source,
                    "shared_cash",
                )
                return result
            assert agent is not None
            persisted = self.repository.persist_shared_cash(canonical, agent, scenario_run)
            self.repository.persist_audit(
                action="validation.record_accepted",
                entity_type="shared_cash",
                entity_id=persisted.id,
                provider=None,
                correlation_id=canonical.source,
                findings=findings,
                metadata={"disposition": result.disposition.value},
            )
            return replace(result, persisted_id=str(persisted.id))

    def validate_feed_status(self, record: CanonicalFeedStatusInput) -> ValidationResult:
        canonical = canonical_feed_status(record)
        provider = self.repository.provider_by_code(canonical.provider_code)
        agent = (
            None
            if canonical.agent_ref is None
            else self.repository.agent_by_ref(canonical.agent_ref)
        )
        findings = validate_feed_status_input(canonical, self.settings, provider, agent)
        return _result(canonical, findings)

    def evaluate_feed_quality(self, record: CanonicalFeedStatusInput) -> ValidationResult:
        canonical = canonical_feed_status(record)
        with self.session.begin():
            provider = self.repository.provider_by_code(canonical.provider_code)
            agent = (
                None
                if canonical.agent_ref is None
                else self.repository.agent_by_ref(canonical.agent_ref)
            )
            findings = validate_feed_status_input(canonical, self.settings, provider, agent)
            result = _result(canonical, findings)
            scenario_run = self.repository.scenario_run_by_ref(canonical.scenario_run_ref)
            if provider is None:
                return result
            feed = self.repository.persist_feed_status(
                canonical,
                provider,
                agent,
                scenario_run,
                status_for_findings(findings),
            )
            self.repository.persist_quality_events(feed, findings)
            action = _feed_action(status_for_findings(findings))
            self.repository.persist_audit(
                action=action,
                entity_type="provider_feed_status",
                entity_id=feed.id,
                provider=provider,
                correlation_id=f"{canonical.provider_code}-feed",
                findings=findings,
                metadata={"quality_score": str(result.quality_score.overall_score)},
            )
            return replace(result, persisted_id=str(feed.id))

    def ingest_simulated_provider_record(self, record: SimulatedProviderRecord) -> ValidationResult:
        canonical = SimulatedProviderAdapter(record.provider_code).map_record(record)
        return self.ingest_canonical(canonical)

    def ingest_canonical(self, record: CanonicalRecord) -> ValidationResult:
        if isinstance(record, CanonicalTransactionInput):
            return self.ingest_transaction(record)
        if isinstance(record, CanonicalProviderBalanceInput):
            return self.ingest_provider_balance(record)
        if isinstance(record, CanonicalSharedCashInput):
            return self.ingest_shared_cash(record)
        return self.evaluate_feed_quality(record)

    def _persist_warning_if_needed(
        self,
        provider: Provider | None,
        agent: Agent | None,
        scenario_run: ScenarioRun | None,
        findings: tuple[ValidationFinding, ...],
    ) -> None:
        warning_findings = tuple(
            item for item in findings if item.usability == RecordUsability.USABLE_WITH_WARNING
        )
        if provider is None or not warning_findings:
            return
        feed = self.repository.synthetic_validation_feed(provider, agent, scenario_run)
        self.repository.persist_quality_events(feed, warning_findings)

    def _persist_rejection(
        self,
        provider: Provider | None,
        agent: Agent | None,
        scenario_run: ScenarioRun | None,
        findings: tuple[ValidationFinding, ...],
        action: str,
        correlation_id: str,
        entity_type: str,
    ) -> None:
        if provider is not None:
            feed = self.repository.synthetic_validation_feed(
                provider,
                agent,
                scenario_run,
                FeedQualityStatus.INVALID,
            )
            self.repository.persist_quality_events(feed, findings)
        self.repository.persist_audit(
            action=action,
            entity_type=entity_type,
            entity_id=None,
            provider=provider,
            correlation_id=correlation_id,
            findings=findings,
            metadata={"disposition": disposition_for(findings).value},
        )


def validation_settings(settings: Settings) -> ValidationSettings:
    currencies = tuple(
        item.strip().upper()
        for item in settings.validation_supported_currencies.split(",")
        if item.strip()
    )
    return ValidationSettings(
        feed_delay_minutes=settings.validation_feed_delay_minutes,
        stale_minutes=settings.validation_stale_minutes,
        future_tolerance_minutes=settings.validation_future_tolerance_minutes,
        timestamp_skew_minutes=settings.validation_timestamp_skew_minutes,
        max_metadata_keys=settings.validation_max_metadata_keys,
        max_metadata_value_length=settings.validation_max_metadata_value_length,
        supported_currencies=currencies or ("BDT",),
    )


def _result(record: object, findings: tuple[ValidationFinding, ...]) -> ValidationResult:
    finding_tuple = tuple(findings)
    disposition = disposition_for(finding_tuple)
    return ValidationResult(
        disposition=disposition,
        usable=disposition in {RecordDisposition.ACCEPTED, RecordDisposition.ACCEPTED_WITH_WARNING},
        findings=finding_tuple,
        quality_score=score_findings(finding_tuple),
        normalized_record=record,
    )


def _feed_action(status: FeedQualityStatus) -> str:
    if status == FeedQualityStatus.DELAYED:
        return "validation.feed_marked_delayed"
    if status == FeedQualityStatus.STALE:
        return "validation.feed_marked_stale"
    if status == FeedQualityStatus.MISSING:
        return "validation.feed_marked_missing"
    if status == FeedQualityStatus.CONFLICTING:
        return "validation.conflict_detected"
    return "validation.quality_score_updated"
