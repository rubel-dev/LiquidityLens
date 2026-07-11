"""Scenario C: Nagad feed goes stale — triggers data quality degradation."""
from core.config import settings


def inject() -> dict:
    # This scenario is controlled via env var NAGAD_DELAY_SECONDS
    # Set it to 300 via FastAPI Cloud dashboard → Save and Redeploy
    # Or patch at runtime for demo purposes
    return {
        "scenario": "data_conflict",
        "instruction": "Set NAGAD_DELAY_SECONDS=300 in FastAPI Cloud env vars to activate Scenario C.",
        "current_delay": settings.NAGAD_DELAY_SECONDS,
    }
