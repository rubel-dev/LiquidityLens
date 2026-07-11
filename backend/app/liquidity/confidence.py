from decimal import Decimal

from app.liquidity.schemas import (
    ConfidenceResult,
    DataQualityContext,
    DemandEstimate,
    ForecastConfig,
)

CONFIDENCE_QUANTUM = Decimal("0.0001")


def assess_confidence(
    demand: DemandEstimate,
    data_quality: DataQualityContext,
    config: ForecastConfig,
) -> ConfidenceResult:
    deductions: list[str] = list(data_quality.issues)
    volatility_penalty = min(demand.volatility * Decimal("0.15"), Decimal("0.25"))
    if volatility_penalty > 0:
        deductions.append(f"volatility penalty {volatility_penalty.quantize(CONFIDENCE_QUANTUM)}")

    history_gap = max(0, config.target_transactions - demand.transaction_count)
    history_penalty = min(Decimal(history_gap) * Decimal("0.03"), Decimal("0.20"))
    if history_penalty > 0:
        deductions.append(f"limited-history penalty {history_penalty.quantize(CONFIDENCE_QUANTUM)}")

    base = max(Decimal("0.00"), Decimal("1.00") - volatility_penalty - history_penalty)
    score = max(Decimal("0.00"), min(Decimal("1.00"), base * data_quality.multiplier))
    quantized = score.quantize(CONFIDENCE_QUANTUM)
    tier = "high" if quantized >= Decimal("0.75") else "medium"
    if quantized < Decimal("0.50"):
        tier = "low"
    return ConfidenceResult(
        score=quantized,
        tier=tier,
        data_quality_multiplier=data_quality.multiplier.quantize(CONFIDENCE_QUANTUM),
        deductions=tuple(deductions),
    )
