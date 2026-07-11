from datetime import timedelta
from decimal import Decimal

from app.anomaly.evidence import fingerprint_evidence
from app.anomaly.exceptions import InvalidAnomalyInputError
from app.anomaly.schemas import (
    RULE_NAME,
    AnomalyFindingResult,
    AnomalyRequest,
    AnomalyTransaction,
    FindingSeverity,
)
from app.confidence.engine import assess_signal_confidence
from app.confidence.schemas import SignalConfidenceInput

SCORE_QUANTUM = Decimal("0.0001")


def detect_near_identical_velocity(
    request: AnomalyRequest,
) -> AnomalyFindingResult | None:
    if request.detected_at.tzinfo is None:
        raise InvalidAnomalyInputError("anomaly detection timestamp must be timezone-aware")
    if request.config.rolling_window_minutes <= 0:
        raise InvalidAnomalyInputError("rolling anomaly window must be positive")

    scoped = tuple(
        item
        for item in request.transactions
        if item.agent_id == request.agent_id and item.provider_id == request.provider_id
    )
    active_start = request.detected_at - timedelta(minutes=request.config.rolling_window_minutes)
    active = tuple(
        item for item in scoped if active_start <= item.occurred_at <= request.detected_at
    )
    if len(active) < request.config.minimum_cash_out_count:
        return None

    cluster = _largest_amount_cluster(active, request.config.amount_similarity_pct)
    group_size = len({item.synthetic_customer_ref for item in cluster})
    baseline_start = active_start - timedelta(days=request.config.baseline_window_days)
    baseline = tuple(item for item in scoped if baseline_start <= item.occurred_at < active_start)
    baseline_windows = max(
        Decimal("1"),
        Decimal(request.config.baseline_window_days * 24 * 60)
        / Decimal(request.config.rolling_window_minutes),
    )
    baseline_rate = Decimal(len(baseline)) / baseline_windows
    denominator = max(Decimal("1.00"), baseline_rate)
    velocity_ratio = Decimal(len(active)) / denominator

    repeated = len(cluster) >= request.config.minimum_cash_out_count
    velocity_spike = velocity_ratio >= request.config.velocity_multiplier
    concentrated = group_size <= request.config.maximum_synthetic_group_size
    if not (repeated and velocity_spike and concentrated):
        return None

    missing_baseline = not baseline
    evidence_coverage = Decimal("0.85") if missing_baseline else Decimal("1.00")
    intrinsic_score = (
        Decimal("0.25")
        + Decimal("0.30")
        + Decimal("0.20")
        + Decimal("0.10")
        + (Decimal("0.00") if missing_baseline else Decimal("0.15"))
    )
    confidence_result = assess_signal_confidence(
        SignalConfidenceInput(
            base_score=intrinsic_score,
            data_quality_multiplier=request.data_quality.multiplier,
            evidence_coverage=evidence_coverage,
            uncertainty=request.data_quality.issues,
        )
    )
    confidence = confidence_result.score
    score = min(
        Decimal("1.00"),
        intrinsic_score
        + min(Decimal("0.15"), (velocity_ratio - request.config.velocity_multiplier) / 20),
    ).quantize(SCORE_QUANTUM)
    severity = _severity(score)
    threshold_rank = {
        FindingSeverity.LOW: 0,
        FindingSeverity.MEDIUM: 1,
        FindingSeverity.HIGH: 2,
    }
    requires_review = (
        request.data_quality.complete
        and confidence >= request.config.minimum_confidence_to_review
        and threshold_rank[severity] >= threshold_rank[request.config.review_severity_threshold]
    )
    uncertainty = list(request.data_quality.issues)
    if missing_baseline:
        uncertainty.append("Prior provider baseline is unavailable; confidence is reduced.")
    if request.event_context in {"eid", "salary_day"}:
        uncertainty.append(
            "Seasonal context may explain increased demand; human context is required."
        )
    recommendation = (
        "Human review is recommended; this deterministic pattern is not proof of wrongdoing."
        if requires_review
        else "Continue monitoring; current evidence or confidence is insufficient for review."
    )
    amounts = tuple(item.amount for item in cluster)
    evidence = fingerprint_evidence(
        cluster_count=len(cluster),
        cluster_low=min(amounts),
        cluster_high=max(amounts),
        active_count=len(active),
        baseline_rate=baseline_rate.quantize(SCORE_QUANTUM),
        velocity_ratio=velocity_ratio.quantize(SCORE_QUANTUM),
        group_size=group_size,
        window_minutes=request.config.rolling_window_minutes,
    )
    return AnomalyFindingResult(
        agent_id=request.agent_id,
        provider_id=request.provider_id,
        pattern=RULE_NAME,
        severity=severity,
        score=score,
        confidence=confidence,
        confidence_tier=confidence_result.tier,
        requires_review=requires_review,
        evidence=evidence,
        uncertainty=tuple(uncertainty),
        recommendation=recommendation,
        detected_at=request.detected_at,
    )


def _largest_amount_cluster(
    transactions: tuple[AnomalyTransaction, ...], similarity_pct: Decimal
) -> tuple[AnomalyTransaction, ...]:
    best: tuple[AnomalyTransaction, ...] = ()
    for anchor in transactions:
        tolerance = anchor.amount * similarity_pct / Decimal("100")
        cluster = tuple(
            item for item in transactions if abs(item.amount - anchor.amount) <= tolerance
        )
        if len(cluster) > len(best):
            best = cluster
    return best


def _severity(score: Decimal) -> FindingSeverity:
    if score >= Decimal("0.85"):
        return FindingSeverity.HIGH
    if score >= Decimal("0.60"):
        return FindingSeverity.MEDIUM
    return FindingSeverity.LOW
