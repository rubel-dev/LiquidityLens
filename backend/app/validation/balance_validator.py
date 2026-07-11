from decimal import Decimal

from app.persistence.models.agent import Agent, AgentProviderAccount
from app.persistence.models.balance import ProviderBalanceSnapshot
from app.persistence.models.provider import Provider
from app.validation.enums import RecordUsability, ValidationCategory, ValidationSeverity
from app.validation.rules import build_finding, validate_common
from app.validation.schemas import (
    CanonicalProviderBalanceInput,
    CanonicalSharedCashInput,
    ValidationFinding,
    ValidationSettings,
)


def validate_provider_balance_input(
    record: CanonicalProviderBalanceInput,
    settings: ValidationSettings,
    provider: Provider | None,
    agent: Agent | None,
    account: AgentProviderAccount | None,
    duplicate_exists: bool,
    previous: ProviderBalanceSnapshot | None,
) -> tuple[ValidationFinding, ...]:
    findings = validate_common(
        provider_code=record.provider_code,
        agent_ref=record.agent_ref,
        record_id=record.account_ref,
        timestamps=(record.balance_timestamp, record.received_timestamp),
        metadata=record.source_metadata,
        settings=settings,
    )
    if provider is None:
        findings.append(
            _provider_finding(
                record,
                len(findings),
                ValidationCategory.UNKNOWN_PROVIDER,
                "known provider",
                record.provider_code,
            )
        )
    if agent is None:
        findings.append(
            _provider_finding(
                record,
                len(findings),
                ValidationCategory.MISSING_REQUIRED_FIELD,
                "known agent",
                record.agent_ref,
            )
        )
    if account is None:
        findings.append(
            _provider_finding(
                record,
                len(findings),
                ValidationCategory.MISSING_REQUIRED_FIELD,
                "known account",
                record.account_ref,
            )
        )
    elif provider is not None and account.provider_id != provider.id:
        findings.append(
            _provider_finding(
                record,
                len(findings),
                ValidationCategory.PROVIDER_SCOPE_MISMATCH,
                "account provider matches record provider",
                record.account_ref,
            )
        )
    elif agent is not None and account.agent_id != agent.id:
        findings.append(
            _provider_finding(
                record,
                len(findings),
                ValidationCategory.AGENT_ACCOUNT_MISMATCH,
                "account agent matches record agent",
                record.account_ref,
            )
        )
    if duplicate_exists:
        findings.append(
            _provider_warning(
                record,
                len(findings),
                ValidationCategory.DUPLICATE_SNAPSHOT,
                "unique balance timestamp",
                record.balance_timestamp.isoformat(),
            )
        )
    if record.reported_balance is not None and record.reported_balance < Decimal("0.00"):
        findings.append(
            _provider_finding(
                record,
                len(findings),
                ValidationCategory.NEGATIVE_BALANCE,
                "non-negative balance or null unknown",
                str(record.reported_balance),
            )
        )
    conflicting_same_point = (
        previous is not None
        and previous.amount != record.reported_balance
        and previous.observed_at == record.balance_timestamp
    )
    if conflicting_same_point:
        findings.append(
            _provider_quarantine(
                record,
                len(findings),
                ValidationCategory.CONFLICTING_BALANCE,
                "same logical snapshot has same value",
                str(record.reported_balance),
            )
        )
    if previous is not None and record.balance_timestamp < previous.observed_at:
        findings.append(
            _provider_warning(
                record,
                len(findings),
                ValidationCategory.OUT_OF_ORDER_EVENT,
                "monotonic balance timestamp",
                record.balance_timestamp.isoformat(),
            )
        )
    return tuple(findings)


def validate_shared_cash_input(
    record: CanonicalSharedCashInput,
    settings: ValidationSettings,
    agent: Agent | None,
    duplicate_exists: bool,
) -> tuple[ValidationFinding, ...]:
    findings = validate_common(
        provider_code=None,
        agent_ref=record.agent_ref,
        record_id=record.source,
        timestamps=(record.snapshot_timestamp, record.received_timestamp),
        metadata=record.source_metadata,
        settings=settings,
    )
    if agent is None:
        findings.append(
            _cash_finding(
                record,
                len(findings),
                ValidationCategory.MISSING_REQUIRED_FIELD,
                "known agent",
                record.agent_ref,
            )
        )
    if duplicate_exists:
        findings.append(
            _cash_warning(
                record,
                len(findings),
                ValidationCategory.DUPLICATE_SNAPSHOT,
                "unique cash timestamp",
                record.snapshot_timestamp.isoformat(),
            )
        )
    if record.reported_cash is not None and record.reported_cash < Decimal("0.00"):
        findings.append(
            _cash_finding(
                record,
                len(findings),
                ValidationCategory.NEGATIVE_BALANCE,
                "non-negative cash or null unknown",
                str(record.reported_cash),
            )
        )
    return tuple(findings)


def _provider_finding(
    record,
    index: int,
    category: ValidationCategory,
    expected: str,
    observed: str,
):
    return build_finding(
        index=index + 1,
        rule_id=f"VAL-BAL-{index + 1:03d}",
        category=category,
        severity=ValidationSeverity.HIGH,
        provider_scope=record.provider_code,
        agent_scope=record.agent_ref,
        source_record_id=record.account_ref,
        fields=("provider_balance",),
        expected=expected,
        observed=observed,
        timestamp=record.received_timestamp,
        usability=RecordUsability.REJECTED,
    )


def _provider_warning(
    record,
    index: int,
    category: ValidationCategory,
    expected: str,
    observed: str,
):
    return build_finding(
        index=index + 1,
        rule_id=f"VAL-BAL-{index + 1:03d}",
        category=category,
        severity=ValidationSeverity.LOW,
        provider_scope=record.provider_code,
        agent_scope=record.agent_ref,
        source_record_id=record.account_ref,
        fields=("provider_balance",),
        expected=expected,
        observed=observed,
        timestamp=record.received_timestamp,
        usability=RecordUsability.USABLE_WITH_WARNING,
    )


def _provider_quarantine(
    record,
    index: int,
    category: ValidationCategory,
    expected: str,
    observed: str,
):
    return build_finding(
        index=index + 1,
        rule_id=f"VAL-BAL-{index + 1:03d}",
        category=category,
        severity=ValidationSeverity.MEDIUM,
        provider_scope=record.provider_code,
        agent_scope=record.agent_ref,
        source_record_id=record.account_ref,
        fields=("provider_balance",),
        expected=expected,
        observed=observed,
        timestamp=record.received_timestamp,
        usability=RecordUsability.QUARANTINED,
    )


def _cash_finding(record, index: int, category: ValidationCategory, expected: str, observed: str):
    return build_finding(
        index=index + 1,
        rule_id=f"VAL-CASH-{index + 1:03d}",
        category=category,
        severity=ValidationSeverity.HIGH,
        provider_scope=None,
        agent_scope=record.agent_ref,
        source_record_id=record.source,
        fields=("shared_cash",),
        expected=expected,
        observed=observed,
        timestamp=record.received_timestamp,
        usability=RecordUsability.REJECTED,
    )


def _cash_warning(record, index: int, category: ValidationCategory, expected: str, observed: str):
    return build_finding(
        index=index + 1,
        rule_id=f"VAL-CASH-{index + 1:03d}",
        category=category,
        severity=ValidationSeverity.LOW,
        provider_scope=None,
        agent_scope=record.agent_ref,
        source_record_id=record.source,
        fields=("shared_cash",),
        expected=expected,
        observed=observed,
        timestamp=record.received_timestamp,
        usability=RecordUsability.USABLE_WITH_WARNING,
    )
