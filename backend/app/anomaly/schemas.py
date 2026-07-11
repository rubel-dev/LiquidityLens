import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from app.persistence.models.enums import FeedQualityStatus

RULE_NAME = "near_identical_cash_out_velocity"
RULE_VERSION = "v1"


class FindingSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class AnomalyRuleConfig:
    amount_similarity_pct: Decimal = Decimal("2.0")
    rolling_window_minutes: int = 30
    velocity_multiplier: Decimal = Decimal("3.0")
    minimum_cash_out_count: int = 5
    maximum_synthetic_group_size: int = 5
    baseline_window_days: int = 7
    minimum_confidence_to_review: Decimal = Decimal("0.50")
    review_severity_threshold: FindingSeverity = FindingSeverity.MEDIUM


@dataclass(frozen=True)
class AnomalyTransaction:
    transaction_id: uuid.UUID
    provider_id: uuid.UUID
    agent_id: uuid.UUID
    synthetic_customer_ref: str
    amount: Decimal
    occurred_at: datetime


@dataclass(frozen=True)
class AnomalyDataQuality:
    multiplier: Decimal = Decimal("1.00")
    complete: bool = True
    statuses: tuple[FeedQualityStatus, ...] = ()
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class AnomalyEvidence:
    evidence_type: str
    label: str
    value: str
    weight: Decimal
    detail: str


@dataclass(frozen=True)
class AnomalyRequest:
    agent_id: uuid.UUID
    provider_id: uuid.UUID
    transactions: tuple[AnomalyTransaction, ...]
    detected_at: datetime
    data_quality: AnomalyDataQuality = field(default_factory=AnomalyDataQuality)
    event_context: str = "standard"
    config: AnomalyRuleConfig = field(default_factory=AnomalyRuleConfig)


@dataclass(frozen=True)
class AnomalyFindingResult:
    agent_id: uuid.UUID
    provider_id: uuid.UUID
    pattern: str
    severity: FindingSeverity
    score: Decimal
    confidence: Decimal
    confidence_tier: str
    requires_review: bool
    evidence: tuple[AnomalyEvidence, ...]
    uncertainty: tuple[str, ...]
    recommendation: str
    detected_at: datetime
    rule_version: str = RULE_VERSION
    finding_id: uuid.UUID | None = None
