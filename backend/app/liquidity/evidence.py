from app.liquidity.schemas import (
    ConfidenceResult,
    DemandEstimate,
    ForecastEvidence,
    ForecastRequest,
)


def build_evidence(
    request: ForecastRequest,
    demand: DemandEstimate,
    confidence: ConfidenceResult,
) -> tuple[ForecastEvidence, ...]:
    evidence = [
        ForecastEvidence(
            "balance",
            "Current known balance",
            "unknown" if request.current_balance is None else str(request.current_balance),
            (
                "Provider-scoped e-money or provider-independent shared cash; "
                "balances are never merged."
            ),
        ),
        ForecastEvidence(
            "demand_window",
            "Rolling demand window",
            f"{request.config.rolling_window_minutes} minutes",
            f"{demand.transaction_count} validated cash-in/cash-out transactions were considered.",
        ),
        ForecastEvidence(
            "net_consumption",
            "Net consumption in window",
            str(demand.net_consumption),
            "Direction follows the documented cash-in/cash-out accounting convention.",
        ),
        ForecastEvidence(
            "demand_rate",
            "Expected consumption rate per minute",
            str(demand.expected_rate_per_minute),
            "Deterministic net rate with bounded volatility and event-context adjustments.",
        ),
        ForecastEvidence(
            "volatility",
            "Volatility adjustment",
            str(demand.volatility_uplift),
            f"Observed coefficient of variation: {demand.volatility}.",
        ),
        ForecastEvidence(
            "event_context",
            "Event context",
            request.event_context.value,
            f"Applied deterministic multiplier {demand.event_multiplier}.",
        ),
        ForecastEvidence(
            "data_quality",
            "Data-quality confidence multiplier",
            str(confidence.data_quality_multiplier),
            "; ".join(request.data_quality.issues) or "No active data-quality deductions.",
        ),
    ]
    return tuple(evidence)
