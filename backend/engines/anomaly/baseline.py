"""Calendar-aware baseline multipliers — suppresses false positives on Eid/salary days."""
from datetime import datetime

DEMAND_MULTIPLIERS = {
    "eid":        3.0,
    "eid_before": 2.5,
    "salary_day": 1.8,
    "friday":     1.3,
    "weekend":    0.8,
    "weekday":    1.0,
}


def get_day_type(dt: datetime) -> str:
    day = dt.day
    weekday = dt.weekday()
    if day in (1, 25, 26, 27, 28, 29, 30):
        return "salary_day"
    if weekday == 4:
        return "friday"
    if weekday in (5, 6):
        return "weekend"
    return "weekday"


def get_threshold_multiplier(dt: datetime | None = None) -> float:
    now = dt or datetime.utcnow()
    day_type = get_day_type(now)
    return DEMAND_MULTIPLIERS.get(day_type, 1.0)
