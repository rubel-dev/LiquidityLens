import time
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.liquidity.forecast import calculate_forecast
from app.liquidity.schemas import (
    DemandTransaction,
    ForecastRequest,
    ForecastScope,
)
from app.persistence.models.enums import TransactionType

AGENT_ID = uuid.UUID("00000000-0000-0000-0000-000000000101")
PROVIDER_ID = uuid.UUID("00000000-0000-0000-0000-000000000102")
GENERATED_AT = datetime(2026, 7, 11, 11, 0, tzinfo=UTC)


def evaluation_request() -> ForecastRequest:
    transactions = tuple(
        DemandTransaction(
            provider_id=PROVIDER_ID,
            transaction_type=TransactionType.CASH_IN,
            amount=Decimal("100.00"),
            occurred_at=GENERATED_AT - timedelta(minutes=minutes_ago),
        )
        for minutes_ago in (90, 60, 30)
    )
    return ForecastRequest(
        agent_id=AGENT_ID,
        provider_id=PROVIDER_ID,
        scope=ForecastScope.PROVIDER_E_MONEY,
        current_balance=Decimal("100.00"),
        transactions=transactions,
        generated_at=GENERATED_AT,
    )


def test_synthetic_forecast_error_and_shortage_detection_lead_time() -> None:
    result = calculate_forecast(evaluation_request())
    actual_shortage_at = GENERATED_AT + timedelta(minutes=40)

    assert result.estimated_shortage_at is not None
    forecast_error_minutes = abs(
        (result.estimated_shortage_at - actual_shortage_at).total_seconds() / 60
    )
    lead_time_minutes = (actual_shortage_at - GENERATED_AT).total_seconds() / 60
    print(
        "LIQUIDITY_ACCURACY "
        f"forecast_error_minutes={forecast_error_minutes:.4f} "
        f"shortage_detection_lead_time_minutes={lead_time_minutes:.4f}"
    )

    assert forecast_error_minutes == 0
    assert lead_time_minutes >= 30


def test_deterministic_forecast_average_and_p95_processing_latency() -> None:
    request = evaluation_request()
    durations_ms: list[float] = []
    for _ in range(250):
        start = time.perf_counter_ns()
        calculate_forecast(request)
        durations_ms.append((time.perf_counter_ns() - start) / 1_000_000)

    ordered = sorted(durations_ms)
    average_ms = sum(durations_ms) / len(durations_ms)
    p95_ms = ordered[int(len(ordered) * 0.95) - 1]
    print(f"LIQUIDITY_LATENCY average_ms={average_ms:.4f} p95_ms={p95_ms:.4f} runs=250")

    assert average_ms < 10
    assert p95_ms < 20
