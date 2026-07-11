from decimal import Decimal

from app.validation.enums import (
    QualityLevel,
    RecordDisposition,
    RecordUsability,
    ValidationCategory,
)
from app.validation.schemas import DataQualityScore, ValidationFinding

PENALTIES: dict[ValidationCategory, Decimal] = {
    ValidationCategory.VALID: Decimal("0.00"),
    ValidationCategory.DUPLICATE_TRANSACTION: Decimal("0.00"),
    ValidationCategory.DUPLICATE_SNAPSHOT: Decimal("0.05"),
    ValidationCategory.DELAYED_FEED: Decimal("0.15"),
    ValidationCategory.STALE_FEED: Decimal("0.25"),
    ValidationCategory.MISSING_FEED: Decimal("0.40"),
    ValidationCategory.CONFLICTING_BALANCE: Decimal("0.35"),
    ValidationCategory.SEQUENCE_GAP: Decimal("0.20"),
    ValidationCategory.OUT_OF_ORDER_EVENT: Decimal("0.15"),
}

DEFAULT_PENALTY = Decimal("0.50")


def score_findings(findings: tuple[ValidationFinding, ...]) -> DataQualityScore:
    if not findings:
        score = Decimal("1.00")
    else:
        total_penalty = sum(
            (PENALTIES.get(item.category, DEFAULT_PENALTY) for item in findings),
            Decimal("0.00"),
        )
        score = max(Decimal("0.00"), Decimal("1.00") - total_penalty)
    if score >= Decimal("0.85"):
        level = QualityLevel.HIGH
        recommendation = "Safe for downstream validation-aware analysis."
    elif score >= Decimal("0.65"):
        level = QualityLevel.MEDIUM
        recommendation = "Usable with warnings; reduce downstream confidence."
    elif score >= Decimal("0.35"):
        level = QualityLevel.LOW
        recommendation = "Use only with caution; require review before confident conclusions."
    else:
        level = QualityLevel.UNUSABLE
        recommendation = "Do not use as trusted input."
    return DataQualityScore(
        overall_score=score.quantize(Decimal("0.01")),
        quality_level=level,
        component_scores={
            "completeness": _component_score(findings, "missing"),
            "freshness": _component_score(findings, "feed"),
            "consistency": _component_score(findings, "conflicting"),
            "identity": _component_score(findings, "identifier"),
            "timestamp": _component_score(findings, "timestamp"),
        },
        triggered_rules=tuple(item.rule_id for item in findings),
        evidence=tuple(item.evidence for item in findings),
        confidence_multiplier=score.quantize(Decimal("0.01")),
        safe_use_recommendation=recommendation,
    )


def disposition_for(findings: tuple[ValidationFinding, ...]) -> RecordDisposition:
    if not findings:
        return RecordDisposition.ACCEPTED
    if any(item.category == ValidationCategory.DUPLICATE_TRANSACTION for item in findings):
        return RecordDisposition.DUPLICATE_IGNORED
    if any(item.usability == RecordUsability.REJECTED for item in findings):
        return RecordDisposition.REJECTED
    if any(item.usability == RecordUsability.QUARANTINED for item in findings):
        return RecordDisposition.QUARANTINED
    return RecordDisposition.ACCEPTED_WITH_WARNING


def _component_score(findings: tuple[ValidationFinding, ...], keyword: str) -> Decimal:
    count = sum(
        1 for item in findings if keyword in item.category.value or keyword in item.rule_id.lower()
    )
    raw_score = Decimal("1.00") - (Decimal(count) * Decimal("0.25"))
    return max(Decimal("0.00"), raw_score).quantize(Decimal("0.01"))
