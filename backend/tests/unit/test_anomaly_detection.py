import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.anomaly.detector import detect_near_identical_velocity
from app.anomaly.exceptions import InvalidAnomalyInputError
from app.anomaly.schemas import (
    AnomalyDataQuality,
    AnomalyRequest,
    AnomalyTransaction,
    FindingSeverity,
)
from app.persistence.models.enums import FeedQualityStatus

AGENT_ID = uuid.UUID("00000000-0000-0000-0000-000000000201")
PROVIDER_A = uuid.UUID("00000000-0000-0000-0000-000000000202")
PROVIDER_B = uuid.UUID("00000000-0000-0000-0000-000000000203")
NOW = datetime(2026, 7, 11, 11, 0, tzinfo=UTC)


def tx(
    index: int,
    *,
    amount: str = "1000.00",
    minutes_ago: int,
    provider_id: uuid.UUID = PROVIDER_A,
    customer_index: int | None = None,
) -> AnomalyTransaction:
    return AnomalyTransaction(
        transaction_id=uuid.UUID(int=1000 + index),
        provider_id=provider_id,
        agent_id=AGENT_ID,
        synthetic_customer_ref=f"SIM-CUST-{customer_index or ((index % 3) + 1):04d}",
        amount=Decimal(amount),
        occurred_at=NOW - timedelta(minutes=minutes_ago),
    )


def positive_transactions() -> tuple[AnomalyTransaction, ...]:
    baseline = (
        tx(100, amount="400.00", minutes_ago=180),
        tx(101, amount="700.00", minutes_ago=120),
    )
    active = tuple(
        tx(index, amount=str(995 + index), minutes_ago=25 - (index * 4)) for index in range(6)
    )
    return baseline + active


def request(
    transactions: tuple[AnomalyTransaction, ...] | None = None,
    quality: AnomalyDataQuality | None = None,
    context: str = "standard",
) -> AnomalyRequest:
    return AnomalyRequest(
        agent_id=AGENT_ID,
        provider_id=PROVIDER_A,
        transactions=positive_transactions() if transactions is None else transactions,
        detected_at=NOW,
        data_quality=quality or AnomalyDataQuality(),
        event_context=context,
    )


def test_repeated_amount_and_velocity_spike_produce_fingerprint() -> None:
    finding = detect_near_identical_velocity(request())

    assert finding is not None
    assert finding.severity == FindingSeverity.HIGH
    assert finding.requires_review is True
    assert {item.evidence_type for item in finding.evidence} == {
        "repeated_amount",
        "velocity",
        "concentrated_group",
        "time_window_deviation",
        "baseline_deviation",
    }
    assert any("6 events" in item.value for item in finding.evidence)


def test_provider_balances_and_transactions_remain_isolated() -> None:
    other_provider = tuple(
        tx(index, minutes_ago=25 - index * 4, provider_id=PROVIDER_B) for index in range(6)
    )

    assert detect_near_identical_velocity(request(other_provider)) is None


def test_repeated_amount_without_velocity_or_minimum_count_does_not_flag() -> None:
    too_few = tuple(tx(index, minutes_ago=20 - index * 4) for index in range(4))

    assert detect_near_identical_velocity(request(too_few)) is None


def test_velocity_without_repeated_amounts_does_not_flag() -> None:
    varied = tuple(
        tx(index, amount=str(100 + index * 300), minutes_ago=25 - index * 4) for index in range(6)
    )

    assert detect_near_identical_velocity(request(varied)) is None


def test_delayed_feed_reduces_confidence() -> None:
    normal = detect_near_identical_velocity(request())
    delayed = detect_near_identical_velocity(
        request(
            quality=AnomalyDataQuality(
                multiplier=Decimal("0.80"),
                complete=True,
                statuses=(FeedQualityStatus.DELAYED,),
                issues=("delayed provider feed",),
            )
        )
    )

    assert normal is not None and delayed is not None
    assert delayed.confidence < normal.confidence
    assert "delayed provider feed" in delayed.uncertainty


def test_missing_feed_reduces_confidence_and_suppresses_review() -> None:
    finding = detect_near_identical_velocity(
        request(
            quality=AnomalyDataQuality(
                multiplier=Decimal("0.60"),
                complete=False,
                statuses=(FeedQualityStatus.MISSING,),
                issues=("missing provider feed",),
            )
        )
    )

    assert finding is not None
    assert finding.confidence < Decimal("0.75")
    assert finding.requires_review is False
    assert "insufficient" in finding.recommendation


def test_eid_broad_demand_does_not_automatically_become_finding() -> None:
    broad = tuple(
        tx(
            index,
            amount="1000.00",
            minutes_ago=25 - index * 4,
            customer_index=index + 1,
        )
        for index in range(6)
    )

    assert detect_near_identical_velocity(request(broad, context="eid")) is None


def test_seasonal_context_is_uncertainty_not_a_final_decision() -> None:
    finding = detect_near_identical_velocity(request(context="eid"))

    assert finding is not None
    assert any("Seasonal context" in item for item in finding.uncertainty)
    assert "proof of wrongdoing" in finding.recommendation


def test_anomaly_output_is_deterministic() -> None:
    active_request = request()

    assert detect_near_identical_velocity(active_request) == detect_near_identical_velocity(
        active_request
    )


def test_naive_detection_time_is_rejected() -> None:
    active_request = request()
    naive = AnomalyRequest(**{**active_request.__dict__, "detected_at": NOW.replace(tzinfo=None)})

    with pytest.raises(InvalidAnomalyInputError, match="timezone-aware"):
        detect_near_identical_velocity(naive)
