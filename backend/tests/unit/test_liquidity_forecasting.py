import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.liquidity.demand import estimate_demand
from app.liquidity.exceptions import InvalidForecastInputError
from app.liquidity.forecast import calculate_forecast
from app.liquidity.schemas import (
    DataQualityContext,
    DemandTransaction,
    EventContext,
    ForecastConfig,
    ForecastRequest,
    ForecastScope,
    RiskLevel,
)
from app.persistence.models.enums import FeedQualityStatus, TransactionType

AGENT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
PROVIDER_A = uuid.UUID("00000000-0000-0000-0000-000000000010")
PROVIDER_B = uuid.UUID("00000000-0000-0000-0000-000000000020")
NOW = datetime(2026, 7, 11, 11, 0, tzinfo=UTC)


def transaction(
    amount: str,
    transaction_type: TransactionType,
    minutes_ago: int,
    provider_id: uuid.UUID = PROVIDER_A,
) -> DemandTransaction:
    return DemandTransaction(
        provider_id=provider_id,
        transaction_type=transaction_type,
        amount=Decimal(amount),
        occurred_at=NOW - timedelta(minutes=minutes_ago),
    )


def provider_request(
    balance: Decimal | None = Decimal("1000.00"),
    transactions: tuple[DemandTransaction, ...] | None = None,
    quality: DataQualityContext | None = None,
    context: EventContext = EventContext.STANDARD,
    config: ForecastConfig | None = None,
) -> ForecastRequest:
    active_transactions = (
        (
            transaction("100.00", TransactionType.CASH_IN, 90),
            transaction("100.00", TransactionType.CASH_IN, 60),
            transaction("100.00", TransactionType.CASH_IN, 30),
        )
        if transactions is None
        else transactions
    )
    return ForecastRequest(
        agent_id=AGENT_ID,
        provider_id=PROVIDER_A,
        scope=ForecastScope.PROVIDER_E_MONEY,
        current_balance=balance,
        transactions=active_transactions,
        generated_at=NOW,
        data_quality=quality or DataQualityContext(),
        event_context=context,
        config=config or ForecastConfig(),
    )


def test_healthy_provider_balance_uses_decimal_runway() -> None:
    result = calculate_forecast(provider_request(balance=Decimal("10000.00")))

    assert result.risk_level == RiskLevel.HEALTHY
    assert result.runway_minutes == Decimal("4000.00")
    assert result.estimated_shortage_at is None
    assert isinstance(result.expected_demand_rate_per_minute, Decimal)


def test_hidden_provider_shortage_is_critical_and_timezone_aware() -> None:
    result = calculate_forecast(provider_request(balance=Decimal("50.00")))

    assert result.risk_level == RiskLevel.CRITICAL
    assert result.runway_minutes == Decimal("20.00")
    assert result.estimated_shortage_at == NOW + timedelta(minutes=20)
    assert result.estimated_shortage_at.tzinfo is not None


def test_shared_cash_uses_cash_out_as_consumption() -> None:
    cash_outs = (
        transaction("120.00", TransactionType.CASH_OUT, 90),
        transaction("120.00", TransactionType.CASH_OUT, 60, PROVIDER_B),
        transaction("120.00", TransactionType.CASH_OUT, 30),
    )
    result = calculate_forecast(
        ForecastRequest(
            agent_id=AGENT_ID,
            provider_id=None,
            scope=ForecastScope.SHARED_CASH,
            current_balance=Decimal("60.00"),
            transactions=cash_outs,
            generated_at=NOW,
        )
    )

    assert result.risk_level == RiskLevel.CRITICAL
    assert result.runway_minutes == Decimal("20.00")


def test_provider_accounting_and_provider_isolation() -> None:
    rows = (
        transaction("200.00", TransactionType.CASH_IN, 90),
        transaction("50.00", TransactionType.CASH_OUT, 60),
        transaction("100.00", TransactionType.CASH_IN, 30),
        transaction("9999.00", TransactionType.CASH_IN, 20, PROVIDER_B),
    )
    result = calculate_forecast(provider_request(balance=Decimal("250.00"), transactions=rows))

    assert result.expected_demand_rate_per_minute == Decimal("2.3617")
    assert result.runway_minutes == Decimal("105.86")
    assert result.risk_level == RiskLevel.WATCH


def test_cash_in_and_cash_out_have_opposite_shared_cash_direction() -> None:
    rows = (
        transaction("200.00", TransactionType.CASH_OUT, 90),
        transaction("50.00", TransactionType.CASH_IN, 60),
        transaction("100.00", TransactionType.CASH_OUT, 30),
    )
    estimate = estimate_demand(
        rows,
        ForecastScope.SHARED_CASH,
        NOW,
        EventContext.STANDARD,
        ForecastConfig(),
    )

    assert estimate.net_consumption == Decimal("250.00")
    assert estimate.expected_rate_per_minute > Decimal("2.08")


@pytest.mark.parametrize(
    ("rows", "expected_text"),
    [
        ((), "No validated cash activity"),
        ((transaction("100", TransactionType.CASH_IN, 10),), "below the minimum"),
    ],
)
def test_no_activity_and_insufficient_history_return_unknown(
    rows: tuple[DemandTransaction, ...], expected_text: str
) -> None:
    result = calculate_forecast(provider_request(transactions=rows or None))
    if not rows:
        result = calculate_forecast(provider_request(transactions=()))

    assert result.risk_level == RiskLevel.UNKNOWN
    assert result.runway_minutes is None
    assert result.estimated_shortage_at is None
    assert any(expected_text in limitation for limitation in result.limitations)


def test_missing_balance_remains_unknown_not_zero() -> None:
    result = calculate_forecast(provider_request(balance=None))

    assert result.current_balance is None
    assert result.risk_level == RiskLevel.UNKNOWN
    assert result.estimated_shortage_at is None
    assert "unknown, not zero" in result.limitations[0]


def test_delayed_feed_reduces_confidence_but_can_forecast() -> None:
    result = calculate_forecast(
        provider_request(
            quality=DataQualityContext(
                multiplier=Decimal("0.80"),
                complete=True,
                statuses=(FeedQualityStatus.DELAYED,),
                issues=("delayed provider feed",),
            )
        )
    )

    assert Decimal("0.50") <= result.confidence < Decimal("0.80")
    assert result.risk_level != RiskLevel.UNKNOWN


@pytest.mark.parametrize("status", [FeedQualityStatus.MISSING, FeedQualityStatus.CONFLICTING])
def test_missing_or_conflicting_feed_returns_unknown(status: FeedQualityStatus) -> None:
    result = calculate_forecast(
        provider_request(
            quality=DataQualityContext(
                multiplier=Decimal("0.60"),
                complete=False,
                statuses=(status,),
                issues=(f"{status.value} provider feed",),
            )
        )
    )

    assert result.risk_level == RiskLevel.UNKNOWN
    assert result.estimated_shortage_at is None
    assert "insufficient" in result.limitations[0].lower()


def test_low_data_quality_confidence_suppresses_shortage_time() -> None:
    result = calculate_forecast(
        provider_request(
            quality=DataQualityContext(
                multiplier=Decimal("0.30"),
                complete=True,
                issues=("multiple invalid records",),
            )
        )
    )

    assert result.confidence < Decimal("0.40")
    assert result.risk_level == RiskLevel.UNKNOWN
    assert result.estimated_shortage_at is None


def test_volatile_demand_increases_expected_rate_and_reduces_confidence() -> None:
    stable = provider_request()
    volatile = provider_request(
        transactions=(
            transaction("10.00", TransactionType.CASH_IN, 90),
            transaction("100.00", TransactionType.CASH_IN, 60),
            transaction("500.00", TransactionType.CASH_IN, 30),
        )
    )

    stable_result = calculate_forecast(stable)
    volatile_result = calculate_forecast(volatile)

    assert volatile_result.expected_demand_rate_per_minute > Decimal("5.08")
    assert volatile_result.confidence < stable_result.confidence


def test_eid_context_is_legitimate_demand_adjustment_not_wrongdoing_language() -> None:
    standard = calculate_forecast(provider_request())
    eid = calculate_forecast(provider_request(context=EventContext.EID))

    assert eid.expected_demand_rate_per_minute > standard.expected_demand_rate_per_minute
    assert any(item.value == "eid" for item in eid.evidence)
    serialized = " ".join(item.detail for item in eid.evidence).lower()
    assert "fraud" not in serialized
    assert "wrongdoing" not in serialized


def test_forecast_output_is_deterministic() -> None:
    request = provider_request(balance=Decimal("50.00"))

    assert calculate_forecast(request) == calculate_forecast(request)


def test_naive_generated_timestamp_is_rejected() -> None:
    request = provider_request()
    naive = ForecastRequest(**{**request.__dict__, "generated_at": NOW.replace(tzinfo=None)})

    with pytest.raises(InvalidForecastInputError, match="timezone-aware"):
        calculate_forecast(naive)
