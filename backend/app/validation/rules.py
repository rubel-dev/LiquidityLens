import re
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from app.persistence.models.enums import TransactionType
from app.validation.enums import (
    RecordUsability,
    ValidationCategory,
    ValidationSeverity,
)
from app.validation.schemas import ValidationFinding, ValidationSettings

PHONE_LIKE_RE = re.compile(r"^(\+?880|01[3-9])\d{8,}$")
SECRET_WORDS = {"password", "otp", "pin", "token", "secret", "credential", "nid"}
SAFE_IDENTIFIER_RE = re.compile(r"^SIM-[A-Z0-9-]+-\d{4,6}$|^SIM-PROVIDER-[A-Z]{2}$")


def is_phone_like(value: str) -> bool:
    return bool(PHONE_LIKE_RE.match(value))


def safe_metadata(metadata: dict[str, Any], settings: ValidationSettings) -> bool:
    if len(metadata) > settings.max_metadata_keys:
        return False
    for key, value in metadata.items():
        lower_key = str(key).lower()
        if any(word in lower_key for word in SECRET_WORDS):
            return False
        if isinstance(value, str):
            lower_value = value.lower()
            if len(value) > settings.max_metadata_value_length:
                return False
            if any(word in lower_value for word in SECRET_WORDS):
                return False
    return True


def timestamp_is_aware(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None


def now_utc() -> datetime:
    return datetime.now(UTC)


def build_finding(
    *,
    index: int,
    rule_id: str,
    category: ValidationCategory,
    severity: ValidationSeverity,
    provider_scope: str | None,
    agent_scope: str | None,
    source_record_id: str,
    fields: tuple[str, ...],
    expected: str,
    observed: str,
    timestamp: datetime,
    usability: RecordUsability,
) -> ValidationFinding:
    return ValidationFinding(
        finding_id=f"SIM-FINDING-{index:06d}",
        rule_id=rule_id,
        category=category,
        severity=severity,
        provider_scope=provider_scope,
        agent_scope=agent_scope,
        source_record_id=source_record_id,
        fields=fields,
        expected=expected,
        observed=observed,
        timestamp=timestamp,
        evidence=f"{category.value}: expected {expected}; observed {observed}",
        safe_next_step="Review source data quality before downstream analysis.",
        usability=usability,
    )


def validate_common(
    *,
    provider_code: str | None,
    agent_ref: str | None,
    record_id: str,
    timestamps: tuple[datetime, ...],
    metadata: dict[str, Any],
    settings: ValidationSettings,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    current_time = now_utc()
    for value in [provider_code, agent_ref, record_id]:
        if value and is_phone_like(value):
            findings.append(
                build_finding(
                    index=len(findings) + 1,
                    rule_id="VAL-ID-001",
                    category=ValidationCategory.INVALID_IDENTIFIER,
                    severity=ValidationSeverity.HIGH,
                    provider_scope=provider_code,
                    agent_scope=agent_ref,
                    source_record_id=record_id,
                    fields=("identifier",),
                    expected="synthetic non-phone-like identifier",
                    observed=value,
                    timestamp=current_time,
                    usability=RecordUsability.REJECTED,
                )
            )
    if not safe_metadata(metadata, settings):
        findings.append(
            build_finding(
                index=len(findings) + 1,
                rule_id="VAL-META-001",
                category=ValidationCategory.MALFORMED_METADATA,
                severity=ValidationSeverity.HIGH,
                provider_scope=provider_code,
                agent_scope=agent_ref,
                source_record_id=record_id,
                fields=("source_metadata",),
                expected="safe bounded metadata without secrets",
                observed="unsafe or oversized metadata",
                timestamp=current_time,
                usability=RecordUsability.REJECTED,
            )
        )
    for timestamp in timestamps:
        if not timestamp_is_aware(timestamp):
            findings.append(
                build_finding(
                    index=len(findings) + 1,
                    rule_id="VAL-TIME-001",
                    category=ValidationCategory.TIMESTAMP_SKEW,
                    severity=ValidationSeverity.HIGH,
                    provider_scope=provider_code,
                    agent_scope=agent_ref,
                    source_record_id=record_id,
                    fields=("timestamp",),
                    expected="timezone-aware timestamp",
                    observed="naive timestamp",
                    timestamp=current_time,
                    usability=RecordUsability.REJECTED,
                )
            )
        elif timestamp > current_time + timedelta(minutes=settings.future_tolerance_minutes):
            findings.append(
                build_finding(
                    index=len(findings) + 1,
                    rule_id="VAL-TIME-002",
                    category=ValidationCategory.FUTURE_TIMESTAMP,
                    severity=ValidationSeverity.HIGH,
                    provider_scope=provider_code,
                    agent_scope=agent_ref,
                    source_record_id=record_id,
                    fields=("timestamp",),
                    expected="timestamp within future tolerance",
                    observed=timestamp.isoformat(),
                    timestamp=current_time,
                    usability=RecordUsability.REJECTED,
                )
            )
    return findings


def valid_transaction_type(value: TransactionType | str) -> bool:
    try:
        TransactionType(str(value))
    except ValueError:
        return False
    return True


def decimal_non_negative(value: Decimal | None) -> bool:
    return value is None or value >= Decimal("0.00")
