import uuid
from dataclasses import dataclass
from decimal import Decimal

from app.anomaly.schemas import AnomalyFindingResult
from app.liquidity.schemas import ForecastResult


@dataclass(frozen=True)
class SignalConfidenceInput:
    base_score: Decimal
    data_quality_multiplier: Decimal
    evidence_coverage: Decimal = Decimal("1.00")
    uncertainty: tuple[str, ...] = ()


@dataclass(frozen=True)
class SignalConfidence:
    score: Decimal
    tier: str
    deductions: tuple[str, ...]


@dataclass(frozen=True)
class CoreSignal:
    signal_id: str
    signal_type: str
    confidence: Decimal
    material_risk: bool
    review_required: bool


@dataclass(frozen=True)
class ConfidenceOutcome:
    score: Decimal
    tier: str
    signal_count: int
    weakest_signal: Decimal
    evidence: tuple[str, ...]
    recommendation: str


@dataclass(frozen=True)
class CoreIntelligenceResult:
    agent_id: uuid.UUID
    forecasts: tuple[ForecastResult, ...]
    anomaly_findings: tuple[AnomalyFindingResult, ...]
    confidence: ConfidenceOutcome
    recommendation: str
    confidence_assessment_id: uuid.UUID | None = None
