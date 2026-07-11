from decimal import Decimal

from app.confidence.engine import assess_signal_confidence, fuse_core_confidence
from app.confidence.schemas import CoreSignal, SignalConfidenceInput


def test_data_quality_reduces_signal_confidence() -> None:
    complete = assess_signal_confidence(
        SignalConfidenceInput(
            base_score=Decimal("0.90"),
            data_quality_multiplier=Decimal("1.00"),
        )
    )
    delayed = assess_signal_confidence(
        SignalConfidenceInput(
            base_score=Decimal("0.90"),
            data_quality_multiplier=Decimal("0.80"),
            uncertainty=("delayed provider feed",),
        )
    )

    assert delayed.score < complete.score
    assert delayed.tier == "medium"
    assert any("data-quality multiplier" in item for item in delayed.deductions)


def test_fusion_caps_confidence_near_weakest_signal() -> None:
    outcome = fuse_core_confidence(
        (
            CoreSignal("forecast-1", "liquidity", Decimal("0.90"), False, False),
            CoreSignal("finding-1", "anomaly", Decimal("0.40"), False, False),
        )
    )

    assert outcome.score == Decimal("0.5500")
    assert outcome.weakest_signal == Decimal("0.4000")


def test_review_recommendation_is_advisory_and_not_a_fraud_declaration() -> None:
    outcome = fuse_core_confidence(
        (CoreSignal("finding-1", "anomaly", Decimal("0.80"), False, True),)
    )

    assert "Human review" in outcome.recommendation
    assert "not proof of wrongdoing" in outcome.recommendation
    assert "fraud detected" not in outcome.recommendation.lower()


def test_liquidity_pressure_recommendation_uses_approved_channel() -> None:
    outcome = fuse_core_confidence(
        (CoreSignal("forecast-1", "liquidity", Decimal("0.80"), True, False),)
    )

    assert "approved liquidity support" in outcome.recommendation


def test_no_signals_return_low_confidence_monitoring_outcome() -> None:
    outcome = fuse_core_confidence(())

    assert outcome.score == Decimal("0.0000")
    assert outcome.signal_count == 0
    assert "Insufficient evidence" in outcome.recommendation
