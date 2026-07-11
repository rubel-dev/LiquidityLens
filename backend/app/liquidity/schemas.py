import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from app.persistence.models.enums import FeedQualityStatus, TransactionType

RULE_NAME = "deterministic_liquidity_runway"
RULE_VERSION = "v1"


class ForecastScope(StrEnum):
    PROVIDER_E_MONEY = "provider_e_money"
    SHARED_CASH = "shared_cash"


class RiskLevel(StrEnum):
    HEALTHY = "healthy"
    WATCH = "watch"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class EventContext(StrEnum):
    STANDARD = "standard"
    EID = "eid"
    SALARY_DAY = "salary_day"


class DemandStatus(StrEnum):
    AVAILABLE = "available"
    NO_ACTIVITY = "no_activity"
    INSUFFICIENT_HISTORY = "insufficient_history"


@dataclass(frozen=True)
class ForecastConfig:
    rolling_window_minutes: int = 120
    forecast_horizon_minutes: int = 240
    minimum_transactions: int = 3
    target_transactions: int = 8
    volatility_adjustment: Decimal = Decimal("0.25")
    maximum_volatility_uplift: Decimal = Decimal("0.50")
    minimum_confidence: Decimal = Decimal("0.40")
    critical_runway_minutes: Decimal = Decimal("30")
    warning_runway_minutes: Decimal = Decimal("60")
    event_multipliers: dict[EventContext, Decimal] = field(
        default_factory=lambda: {
            EventContext.STANDARD: Decimal("1.00"),
            EventContext.EID: Decimal("1.10"),
            EventContext.SALARY_DAY: Decimal("1.08"),
        }
    )


@dataclass(frozen=True)
class DemandTransaction:
    provider_id: uuid.UUID
    transaction_type: TransactionType
    amount: Decimal
    occurred_at: datetime


@dataclass(frozen=True)
class DataQualityContext:
    multiplier: Decimal = Decimal("1.00")
    complete: bool = True
    statuses: tuple[FeedQualityStatus, ...] = ()
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class DemandEstimate:
    status: DemandStatus
    raw_rate_per_minute: Decimal
    expected_rate_per_minute: Decimal
    net_consumption: Decimal
    volatility: Decimal
    volatility_uplift: Decimal
    event_multiplier: Decimal
    transaction_count: int
    calculation_start: datetime
    calculation_end: datetime


@dataclass(frozen=True)
class ConfidenceResult:
    score: Decimal
    tier: str
    data_quality_multiplier: Decimal
    deductions: tuple[str, ...]


@dataclass(frozen=True)
class ForecastEvidence:
    evidence_type: str
    label: str
    value: str
    detail: str


@dataclass(frozen=True)
class ForecastRequest:
    agent_id: uuid.UUID
    scope: ForecastScope
    current_balance: Decimal | None
    transactions: tuple[DemandTransaction, ...]
    generated_at: datetime
    provider_id: uuid.UUID | None = None
    event_context: EventContext = EventContext.STANDARD
    data_quality: DataQualityContext = field(default_factory=DataQualityContext)
    config: ForecastConfig = field(default_factory=ForecastConfig)


@dataclass(frozen=True)
class ForecastResult:
    agent_id: uuid.UUID
    provider_id: uuid.UUID | None
    scope: ForecastScope
    current_balance: Decimal | None
    expected_demand_rate_per_minute: Decimal | None
    runway_minutes: Decimal | None
    estimated_shortage_at: datetime | None
    risk_level: RiskLevel
    confidence: Decimal
    confidence_tier: str
    data_quality_impact: str
    calculation_start: datetime
    calculation_end: datetime
    evidence: tuple[ForecastEvidence, ...]
    limitations: tuple[str, ...]
    generated_at: datetime
    rule_version: str = RULE_VERSION
    forecast_id: uuid.UUID | None = None
