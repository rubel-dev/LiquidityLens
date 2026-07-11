import time
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.anomaly.detector import detect_near_identical_velocity
from app.anomaly.schemas import AnomalyRequest, AnomalyTransaction
from app.confidence.engine import fuse_core_confidence
from app.confidence.schemas import CoreSignal

AGENT_ID = uuid.UUID("00000000-0000-0000-0000-000000000301")
PROVIDER_ID = uuid.UUID("00000000-0000-0000-0000-000000000302")
NOW = datetime(2026, 7, 11, 11, 0, tzinfo=UTC)


def transactions(*, repeated: bool, broad: bool = False) -> tuple[AnomalyTransaction, ...]:
    return tuple(
        AnomalyTransaction(
            transaction_id=uuid.UUID(int=3000 + index),
            provider_id=PROVIDER_ID,
            agent_id=AGENT_ID,
            synthetic_customer_ref=f"SIM-CUST-{(index + 1) if broad else ((index % 3) + 1):04d}",
            amount=Decimal(1000 + index if repeated else 100 + index * 300),
            occurred_at=NOW - timedelta(minutes=25 - index * 4),
        )
        for index in range(6)
    )


def anomaly_request(*, repeated: bool, broad: bool = False, context: str = "standard"):
    return AnomalyRequest(
        agent_id=AGENT_ID,
        provider_id=PROVIDER_ID,
        transactions=transactions(repeated=repeated, broad=broad),
        detected_at=NOW,
        event_context=context,
    )


def test_measured_anomaly_precision_recall_and_false_positive_rate() -> None:
    labelled = (
        (anomaly_request(repeated=True), True),
        (anomaly_request(repeated=True), True),
        (anomaly_request(repeated=False), False),
        (anomaly_request(repeated=True, broad=True, context="eid"), False),
    )
    predictions = tuple(detect_near_identical_velocity(item) is not None for item, _ in labelled)
    truths = tuple(truth for _, truth in labelled)
    true_positive = sum(
        predicted and truth for predicted, truth in zip(predictions, truths, strict=True)
    )
    false_positive = sum(
        predicted and not truth for predicted, truth in zip(predictions, truths, strict=True)
    )
    false_negative = sum(
        not predicted and truth for predicted, truth in zip(predictions, truths, strict=True)
    )
    normal_count = sum(not truth for truth in truths)
    precision = Decimal(true_positive) / Decimal(true_positive + false_positive)
    recall = Decimal(true_positive) / Decimal(true_positive + false_negative)
    false_positive_rate = Decimal(false_positive) / Decimal(normal_count)
    print(
        "CORE_ANOMALY_METRICS "
        f"precision={precision:.4f} recall={recall:.4f} "
        f"false_positive_rate={false_positive_rate:.4f} fixtures={len(labelled)}"
    )

    assert precision >= Decimal("0.80")
    assert recall >= Decimal("0.80")
    assert false_positive_rate <= Decimal("0.20")


def test_measured_core_calculation_latency() -> None:
    request = anomaly_request(repeated=True)
    durations_ms: list[float] = []
    for _ in range(250):
        start = time.perf_counter_ns()
        finding = detect_near_identical_velocity(request)
        assert finding is not None
        fuse_core_confidence(
            (
                CoreSignal(
                    "finding",
                    "anomaly",
                    finding.confidence,
                    False,
                    finding.requires_review,
                ),
            )
        )
        durations_ms.append((time.perf_counter_ns() - start) / 1_000_000)
    ordered = sorted(durations_ms)
    average_ms = sum(durations_ms) / len(durations_ms)
    p95_ms = ordered[int(len(ordered) * 0.95) - 1]
    print(f"CORE_LATENCY average_ms={average_ms:.4f} p95_ms={p95_ms:.4f} runs=250")

    assert average_ms < 10
    assert p95_ms < 20
