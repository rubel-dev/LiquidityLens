from datetime import timedelta
from decimal import Decimal

from app.liquidity.confidence import assess_confidence
from app.liquidity.demand import estimate_demand
from app.liquidity.evidence import build_evidence
from app.liquidity.exceptions import InvalidForecastInputError
from app.liquidity.schemas import (
    DemandStatus,
    ForecastConfig,
    ForecastRequest,
    ForecastResult,
    ForecastScope,
    RiskLevel,
)


def calculate_forecast(request: ForecastRequest) -> ForecastResult:
    if request.scope == ForecastScope.PROVIDER_E_MONEY and request.provider_id is None:
        raise InvalidForecastInputError("provider forecast requires provider_id")
    if request.scope == ForecastScope.SHARED_CASH and request.provider_id is not None:
        raise InvalidForecastInputError("shared-cash forecast must remain provider-independent")
    if request.current_balance is not None and request.current_balance < 0:
        raise InvalidForecastInputError("current balance cannot be negative")

    demand = estimate_demand(
        tuple(
            transaction
            for transaction in request.transactions
            if request.scope == ForecastScope.SHARED_CASH
            or transaction.provider_id == request.provider_id
        ),
        request.scope,
        request.generated_at,
        request.event_context,
        request.config,
    )
    confidence = assess_confidence(demand, request.data_quality, request.config)
    limitations: list[str] = []
    risk = RiskLevel.UNKNOWN
    runway: Decimal | None = None
    shortage_at = None

    if request.current_balance is None:
        limitations.append("Current balance is missing and remains unknown, not zero.")
    if not request.data_quality.complete:
        limitations.append("Input feed completeness or consistency is insufficient.")
    if demand.status == DemandStatus.NO_ACTIVITY:
        limitations.append("No validated cash activity exists in the rolling window.")
    if demand.status == DemandStatus.INSUFFICIENT_HISTORY:
        limitations.append("Validated transaction history is below the minimum requirement.")
    if confidence.score < request.config.minimum_confidence:
        limitations.append("Confidence is below the safe forecast threshold.")

    complete = (
        request.current_balance is not None
        and request.data_quality.complete
        and demand.status == DemandStatus.AVAILABLE
        and confidence.score >= request.config.minimum_confidence
    )
    if complete and demand.expected_rate_per_minute <= 0:
        risk = RiskLevel.HEALTHY
        limitations.append("No positive net consumption is projected from the validated window.")
    elif complete and request.current_balance is not None:
        runway = (request.current_balance / demand.expected_rate_per_minute).quantize(
            Decimal("0.01")
        )
        risk = _risk_for(runway, request.config)
        if runway <= Decimal(request.config.forecast_horizon_minutes):
            shortage_at = request.generated_at + timedelta(minutes=float(runway))
        else:
            limitations.append("Estimated depletion is beyond the configured forecast horizon.")

    evidence = build_evidence(request, demand, confidence)
    return ForecastResult(
        agent_id=request.agent_id,
        provider_id=request.provider_id,
        scope=request.scope,
        current_balance=request.current_balance,
        expected_demand_rate_per_minute=(
            demand.expected_rate_per_minute if demand.status == DemandStatus.AVAILABLE else None
        ),
        runway_minutes=runway,
        estimated_shortage_at=shortage_at,
        risk_level=risk,
        confidence=confidence.score,
        confidence_tier=confidence.tier,
        data_quality_impact=(
            f"multiplier={confidence.data_quality_multiplier}; "
            + ("; ".join(request.data_quality.issues) or "no active deduction")
        ),
        calculation_start=demand.calculation_start,
        calculation_end=demand.calculation_end,
        evidence=evidence,
        limitations=tuple(limitations),
        generated_at=request.generated_at,
    )


def _risk_for(runway: Decimal, config: ForecastConfig) -> RiskLevel:
    if runway <= config.critical_runway_minutes:
        return RiskLevel.CRITICAL
    if runway <= config.warning_runway_minutes:
        return RiskLevel.WARNING
    if runway <= Decimal(config.forecast_horizon_minutes):
        return RiskLevel.WATCH
    return RiskLevel.HEALTHY
