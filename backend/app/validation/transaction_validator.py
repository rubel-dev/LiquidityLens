from datetime import timedelta
from decimal import Decimal

from app.persistence.models.agent import Agent, AgentProviderAccount
from app.persistence.models.provider import Provider
from app.validation.enums import RecordUsability, ValidationCategory, ValidationSeverity
from app.validation.rules import build_finding, valid_transaction_type, validate_common
from app.validation.schemas import CanonicalTransactionInput, ValidationFinding, ValidationSettings


def validate_transaction_input(
    record: CanonicalTransactionInput,
    settings: ValidationSettings,
    provider: Provider | None,
    agent: Agent | None,
    account: AgentProviderAccount | None,
    duplicate_exists: bool,
    latest_transaction_time,
) -> tuple[ValidationFinding, ...]:
    findings = validate_common(
        provider_code=record.provider_code,
        agent_ref=record.agent_ref,
        record_id=record.synthetic_transaction_ref,
        timestamps=(record.event_timestamp, record.received_timestamp),
        metadata=record.source_metadata,
        settings=settings,
    )
    if provider is None:
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.UNKNOWN_PROVIDER,
                "known provider",
                record.provider_code,
            )
        )
    if agent is None:
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.MISSING_REQUIRED_FIELD,
                "known agent",
                record.agent_ref,
            )
        )
    if account is None:
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.MISSING_REQUIRED_FIELD,
                "known account",
                record.account_ref,
            )
        )
    elif provider is not None and account.provider_id != provider.id:
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.PROVIDER_SCOPE_MISMATCH,
                "account provider matches record provider",
                record.account_ref,
            )
        )
    elif agent is not None and account.agent_id != agent.id:
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.AGENT_ACCOUNT_MISMATCH,
                "account agent matches record agent",
                record.account_ref,
            )
        )
    if duplicate_exists:
        findings.append(
            _warning(
                record,
                len(findings),
                ValidationCategory.DUPLICATE_TRANSACTION,
                "unique transaction id",
                record.synthetic_transaction_ref,
            )
        )
    if record.amount <= Decimal("0.00"):
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.INVALID_AMOUNT,
                "positive amount",
                str(record.amount),
            )
        )
    if record.currency not in settings.supported_currencies:
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.INVALID_CURRENCY,
                str(settings.supported_currencies),
                record.currency,
            )
        )
    if not valid_transaction_type(record.transaction_type):
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.INVALID_TRANSACTION_TYPE,
                "supported transaction type",
                str(record.transaction_type),
            )
        )
    skew_limit = record.received_timestamp + timedelta(minutes=settings.timestamp_skew_minutes)
    if skew_limit < record.event_timestamp:
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.TIMESTAMP_SKEW,
                "received timestamp after event",
                record.received_timestamp.isoformat(),
            )
        )
    if latest_transaction_time is not None and record.event_timestamp < latest_transaction_time:
        findings.append(
            _warning(
                record,
                len(findings),
                ValidationCategory.OUT_OF_ORDER_EVENT,
                "monotonic event timestamp",
                record.event_timestamp.isoformat(),
            )
        )
    if record.source_sequence is not None and record.source_sequence < 0:
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.SEQUENCE_GAP,
                "non-negative sequence",
                str(record.source_sequence),
            )
        )
    return tuple(findings)


def _finding(
    record: CanonicalTransactionInput,
    index: int,
    category: ValidationCategory,
    expected: str,
    observed: str,
) -> ValidationFinding:
    return build_finding(
        index=index + 1,
        rule_id=f"VAL-TXN-{index + 1:03d}",
        category=category,
        severity=ValidationSeverity.HIGH,
        provider_scope=record.provider_code,
        agent_scope=record.agent_ref,
        source_record_id=record.synthetic_transaction_ref,
        fields=("transaction",),
        expected=expected,
        observed=observed,
        timestamp=record.received_timestamp,
        usability=RecordUsability.REJECTED,
    )


def _warning(
    record: CanonicalTransactionInput,
    index: int,
    category: ValidationCategory,
    expected: str,
    observed: str,
) -> ValidationFinding:
    return build_finding(
        index=index + 1,
        rule_id=f"VAL-TXN-{index + 1:03d}",
        category=category,
        severity=ValidationSeverity.LOW,
        provider_scope=record.provider_code,
        agent_scope=record.agent_ref,
        source_record_id=record.synthetic_transaction_ref,
        fields=("transaction",),
        expected=expected,
        observed=observed,
        timestamp=record.received_timestamp,
        usability=RecordUsability.USABLE_WITH_WARNING,
    )
