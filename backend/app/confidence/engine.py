from decimal import Decimal

from app.confidence.schemas import (
    ConfidenceOutcome,
    CoreSignal,
    SignalConfidence,
    SignalConfidenceInput,
)

QUANTUM = Decimal("0.0001")


def assess_signal_confidence(value: SignalConfidenceInput) -> SignalConfidence:
    score = max(
        Decimal("0.00"),
        min(
            Decimal("1.00"),
            value.base_score * value.data_quality_multiplier * value.evidence_coverage,
        ),
    ).quantize(QUANTUM)
    deductions = list(value.uncertainty)
    if value.data_quality_multiplier < Decimal("1.00"):
        deductions.append(f"data-quality multiplier {value.data_quality_multiplier}")
    if value.evidence_coverage < Decimal("1.00"):
        deductions.append(f"evidence coverage {value.evidence_coverage}")
    return SignalConfidence(score=score, tier=_tier(score), deductions=tuple(deductions))


def fuse_core_confidence(signals: tuple[CoreSignal, ...]) -> ConfidenceOutcome:
    if not signals:
        return ConfidenceOutcome(
            score=Decimal("0.0000"),
            tier="low",
            signal_count=0,
            weakest_signal=Decimal("0.0000"),
            evidence=("No deterministic intelligence signals were available.",),
            recommendation="Insufficient evidence; continue data collection and monitoring.",
        )
    average = sum((item.confidence for item in signals), Decimal("0.00")) / Decimal(len(signals))
    weakest = min(item.confidence for item in signals)
    score = min(average, weakest + Decimal("0.15")).quantize(QUANTUM)
    review_required = any(item.review_required for item in signals)
    material_risk = any(item.material_risk for item in signals)
    recommendation = "Continue monitoring; no material deterministic pressure is present."
    if material_risk:
        recommendation = (
            "Coordinate approved liquidity support through responsible provider operations."
        )
    if review_required:
        recommendation = (
            "Human review is recommended; unusual activity evidence is not proof of wrongdoing."
        )
    return ConfidenceOutcome(
        score=score,
        tier=_tier(score),
        signal_count=len(signals),
        weakest_signal=weakest.quantize(QUANTUM),
        evidence=tuple(
            f"{item.signal_type}:{item.signal_id} confidence={item.confidence}" for item in signals
        ),
        recommendation=recommendation,
    )


def _tier(score: Decimal) -> str:
    if score >= Decimal("0.75"):
        return "high"
    if score >= Decimal("0.50"):
        return "medium"
    return "low"
