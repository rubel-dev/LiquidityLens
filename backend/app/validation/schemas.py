from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.persistence.models.enums import FeedQualityStatus, TransactionStatus, TransactionType
from app.validation.enums import (
    QualityLevel,
    RecordDisposition,
    RecordUsability,
    ValidationCategory,
    ValidationSeverity,
)


@dataclass(frozen=True)
class ValidationSettings:
    feed_delay_minutes: int = 5
    stale_minutes: int = 15
    future_tolerance_minutes: int = 5
    timestamp_skew_minutes: int = 2
    max_metadata_keys: int = 12
    max_metadata_value_length: int = 120
    supported_currencies: tuple[str, ...] = ("BDT",)


@dataclass(frozen=True)
class CanonicalTransactionInput:
    provider_code: str
    agent_ref: str
    account_ref: str
    synthetic_transaction_ref: str
    synthetic_account_ref: str
    synthetic_customer_ref: str
    transaction_type: TransactionType | str
    amount: Decimal
    currency: str
    event_timestamp: datetime
    received_timestamp: datetime
    source_sequence: int | None = None
    source_status: TransactionStatus | str = TransactionStatus.COMPLETED
    scenario_run_ref: str | None = None
    source_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CanonicalProviderBalanceInput:
    provider_code: str
    agent_ref: str
    account_ref: str
    reported_balance: Decimal | None
    balance_timestamp: datetime
    received_timestamp: datetime
    source_sequence: int | None = None
    availability_state: str = "available"
    scenario_run_ref: str | None = None
    source_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CanonicalSharedCashInput:
    agent_ref: str
    reported_cash: Decimal | None
    snapshot_timestamp: datetime
    received_timestamp: datetime
    source: str
    scenario_run_ref: str | None = None
    source_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CanonicalFeedStatusInput:
    provider_code: str
    agent_ref: str | None
    expected_timestamp: datetime
    received_timestamp: datetime | None
    last_successful_timestamp: datetime | None
    source_status: FeedQualityStatus | str
    source_sequence: int | None = None
    error_code: str | None = None
    scenario_run_ref: str | None = None
    source_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationFinding:
    finding_id: str
    rule_id: str
    category: ValidationCategory
    severity: ValidationSeverity
    provider_scope: str | None
    agent_scope: str | None
    source_record_id: str
    fields: tuple[str, ...]
    expected: str
    observed: str
    timestamp: datetime
    evidence: str
    safe_next_step: str
    usability: RecordUsability


@dataclass(frozen=True)
class DataQualityScore:
    overall_score: Decimal
    quality_level: QualityLevel
    component_scores: dict[str, Decimal]
    triggered_rules: tuple[str, ...]
    evidence: tuple[str, ...]
    confidence_multiplier: Decimal
    safe_use_recommendation: str


@dataclass(frozen=True)
class ValidationResult:
    disposition: RecordDisposition
    usable: bool
    findings: tuple[ValidationFinding, ...]
    quality_score: DataQualityScore
    normalized_record: object | None = None
    persisted_id: str | None = None
