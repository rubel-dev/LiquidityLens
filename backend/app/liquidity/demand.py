from datetime import datetime, timedelta
from decimal import Decimal

from app.liquidity.exceptions import InvalidForecastInputError
from app.liquidity.schemas import (
    DemandEstimate,
    DemandStatus,
    DemandTransaction,
    EventContext,
    ForecastConfig,
    ForecastScope,
)
from app.persistence.models.enums import TransactionType

MONEY_QUANTUM = Decimal("0.0001")


def estimate_demand(
    transactions: tuple[DemandTransaction, ...],
    scope: ForecastScope,
    generated_at: datetime,
    event_context: EventContext,
    config: ForecastConfig,
) -> DemandEstimate:
    if generated_at.tzinfo is None:
        raise InvalidForecastInputError("forecast generated timestamp must be timezone-aware")
    if config.rolling_window_minutes <= 0 or config.minimum_transactions <= 0:
        raise InvalidForecastInputError("forecast window and minimum transactions must be positive")

    calculation_start = generated_at - timedelta(minutes=config.rolling_window_minutes)
    active = tuple(
        item
        for item in transactions
        if calculation_start <= item.occurred_at <= generated_at
        and item.transaction_type in {TransactionType.CASH_IN, TransactionType.CASH_OUT}
    )
    if not active:
        return _empty_estimate(
            DemandStatus.NO_ACTIVITY,
            calculation_start,
            generated_at,
            config,
            event_context,
        )
    if len(active) < config.minimum_transactions:
        return _empty_estimate(
            DemandStatus.INSUFFICIENT_HISTORY,
            calculation_start,
            generated_at,
            config,
            event_context,
            len(active),
        )

    signed_consumption = tuple(_consumption(item, scope) for item in active)
    net_consumption = sum(signed_consumption, Decimal("0.00"))
    raw_rate = max(Decimal("0.00"), net_consumption) / Decimal(config.rolling_window_minutes)
    volatility = _coefficient_of_variation(signed_consumption)
    volatility_uplift = min(
        volatility * config.volatility_adjustment,
        config.maximum_volatility_uplift,
    )
    event_multiplier = config.event_multipliers[event_context]
    expected_rate = raw_rate * (Decimal("1.00") + volatility_uplift) * event_multiplier
    return DemandEstimate(
        status=DemandStatus.AVAILABLE,
        raw_rate_per_minute=raw_rate.quantize(MONEY_QUANTUM),
        expected_rate_per_minute=expected_rate.quantize(MONEY_QUANTUM),
        net_consumption=net_consumption.quantize(Decimal("0.01")),
        volatility=volatility.quantize(MONEY_QUANTUM),
        volatility_uplift=volatility_uplift.quantize(MONEY_QUANTUM),
        event_multiplier=event_multiplier,
        transaction_count=len(active),
        calculation_start=calculation_start,
        calculation_end=generated_at,
    )


def _consumption(transaction: DemandTransaction, scope: ForecastScope) -> Decimal:
    if scope == ForecastScope.PROVIDER_E_MONEY:
        return (
            transaction.amount
            if transaction.transaction_type == TransactionType.CASH_IN
            else -transaction.amount
        )
    return (
        transaction.amount
        if transaction.transaction_type == TransactionType.CASH_OUT
        else -transaction.amount
    )


def _coefficient_of_variation(values: tuple[Decimal, ...]) -> Decimal:
    magnitudes = tuple(abs(value) for value in values)
    if not magnitudes:
        return Decimal("0.00")
    mean = sum(magnitudes, Decimal("0.00")) / Decimal(len(magnitudes))
    if mean == 0:
        return Decimal("0.00")
    variance = sum(((value - mean) ** 2 for value in magnitudes), Decimal("0.00")) / Decimal(
        len(magnitudes)
    )
    return variance.sqrt() / mean


def _empty_estimate(
    status: DemandStatus,
    start: datetime,
    end: datetime,
    config: ForecastConfig,
    event_context: EventContext,
    count: int = 0,
) -> DemandEstimate:
    return DemandEstimate(
        status=status,
        raw_rate_per_minute=Decimal("0.0000"),
        expected_rate_per_minute=Decimal("0.0000"),
        net_consumption=Decimal("0.00"),
        volatility=Decimal("0.0000"),
        volatility_uplift=Decimal("0.0000"),
        event_multiplier=config.event_multipliers[event_context],
        transaction_count=count,
        calculation_start=start,
        calculation_end=end,
    )
