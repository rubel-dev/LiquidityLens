"""Detector 1: transaction velocity — too many transactions in a short window."""
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from providers.base import ProviderTransaction
from .baseline import get_threshold_multiplier

WINDOW_MINUTES = 15
BASE_THRESHOLD = 10   # transactions per window on a normal weekday


@dataclass
class VelocityResult:
    flagged: bool
    count: int
    threshold: int
    window_minutes: int
    multiplier_applied: float
    day_type_note: str


def detect(transactions: list[ProviderTransaction]) -> VelocityResult:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=WINDOW_MINUTES)
    window_txns = [t for t in transactions if t.timestamp >= cutoff]
    count = len(window_txns)

    multiplier = get_threshold_multiplier(now)
    threshold = int(BASE_THRESHOLD * multiplier)

    from .baseline import get_day_type
    day_type = get_day_type(now)

    return VelocityResult(
        flagged=count > threshold,
        count=count,
        threshold=threshold,
        window_minutes=WINDOW_MINUTES,
        multiplier_applied=multiplier,
        day_type_note=f"Threshold adjusted {multiplier}× for {day_type}",
    )
