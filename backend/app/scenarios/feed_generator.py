from datetime import datetime, timedelta

from app.persistence.models.enums import FeedQualityStatus
from app.scenarios.schemas import GeneratedFeedStatus, ScenarioDefinition


def generate_feed_statuses(
    definition: ScenarioDefinition,
    start_timestamp: datetime,
) -> tuple[GeneratedFeedStatus, ...]:
    statuses: list[GeneratedFeedStatus] = []
    for provider_code in ("BK", "NG", "RK"):
        status = FeedQualityStatus.COMPLETE
        observed_at = start_timestamp + timedelta(hours=2)
        ingested_at = observed_at + timedelta(minutes=1)
        event_type = None

        if definition.code == "delayed_feed" and provider_code == "BK":
            status = FeedQualityStatus.DELAYED
            observed_at = start_timestamp + timedelta(minutes=20)
            event_type = "delayed_feed"
        if definition.code == "missing_feed" and provider_code == "NG":
            status = FeedQualityStatus.MISSING
            ingested_at = None
            event_type = "missing_feed"
        if definition.code == "conflicting_balance" and provider_code == "RK":
            status = FeedQualityStatus.CONFLICTING
            event_type = "conflicting_balance"

        statuses.append(
            GeneratedFeedStatus(
                provider_code=provider_code,
                status=status,
                observed_at=observed_at,
                ingested_at=ingested_at,
                event_type=event_type,
            )
        )
    return tuple(statuses)
