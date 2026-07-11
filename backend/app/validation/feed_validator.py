from datetime import timedelta

from app.persistence.models.agent import Agent
from app.persistence.models.enums import FeedQualityStatus
from app.persistence.models.provider import Provider
from app.validation.enums import RecordUsability, ValidationCategory, ValidationSeverity
from app.validation.rules import build_finding, validate_common
from app.validation.schemas import CanonicalFeedStatusInput, ValidationFinding, ValidationSettings


def validate_feed_status_input(
    record: CanonicalFeedStatusInput,
    settings: ValidationSettings,
    provider: Provider | None,
    agent: Agent | None,
) -> tuple[ValidationFinding, ...]:
    timestamps = [record.expected_timestamp]
    if record.received_timestamp is not None:
        timestamps.append(record.received_timestamp)
    if record.last_successful_timestamp is not None:
        timestamps.append(record.last_successful_timestamp)
    findings = validate_common(
        provider_code=record.provider_code,
        agent_ref=record.agent_ref,
        record_id=f"{record.provider_code}-feed",
        timestamps=tuple(timestamps),
        metadata=record.source_metadata,
        settings=settings,
    )
    if provider is None:
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.UNKNOWN_PROVIDER,
                "known provider",
                record.provider_code,
                RecordUsability.REJECTED,
            )
        )
    if record.agent_ref is not None and agent is None:
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.MISSING_REQUIRED_FIELD,
                "known agent",
                record.agent_ref,
                RecordUsability.REJECTED,
            )
        )
    if record.source_status == FeedQualityStatus.MISSING or record.received_timestamp is None:
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.MISSING_FEED,
                "received provider feed",
                "missing",
                RecordUsability.QUARANTINED,
            )
        )
    elif record.received_timestamp > record.expected_timestamp + timedelta(
        minutes=settings.feed_delay_minutes
    ):
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.DELAYED_FEED,
                "feed within delay threshold",
                record.received_timestamp.isoformat(),
                RecordUsability.USABLE_WITH_WARNING,
            )
        )
    stale_delta = None
    if record.last_successful_timestamp is not None:
        stale_delta = record.expected_timestamp - record.last_successful_timestamp
    if stale_delta is not None and stale_delta > timedelta(minutes=settings.stale_minutes):
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.STALE_FEED,
                "fresh provider data",
                record.last_successful_timestamp.isoformat(),
                RecordUsability.USABLE_WITH_WARNING,
            )
        )
    if record.source_status == FeedQualityStatus.CONFLICTING:
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.CONFLICTING_BALANCE,
                "consistent feed values",
                "conflicting",
                RecordUsability.QUARANTINED,
            )
        )
    if record.source_status == FeedQualityStatus.INVALID:
        findings.append(
            _finding(
                record,
                len(findings),
                ValidationCategory.UNSUPPORTED_RECORD,
                "valid feed status",
                "invalid",
                RecordUsability.REJECTED,
            )
        )
    return tuple(findings)


def status_for_findings(findings: tuple[ValidationFinding, ...]) -> FeedQualityStatus:
    categories = {item.category for item in findings}
    if ValidationCategory.MISSING_FEED in categories:
        return FeedQualityStatus.MISSING
    if ValidationCategory.CONFLICTING_BALANCE in categories:
        return FeedQualityStatus.CONFLICTING
    if ValidationCategory.UNSUPPORTED_RECORD in categories:
        return FeedQualityStatus.INVALID
    if ValidationCategory.STALE_FEED in categories:
        return FeedQualityStatus.STALE
    if ValidationCategory.DELAYED_FEED in categories:
        return FeedQualityStatus.DELAYED
    return FeedQualityStatus.COMPLETE


def _finding(
    record: CanonicalFeedStatusInput,
    index: int,
    category: ValidationCategory,
    expected: str,
    observed: str,
    usability: RecordUsability,
) -> ValidationFinding:
    return build_finding(
        index=index + 1,
        rule_id=f"VAL-FEED-{index + 1:03d}",
        category=category,
        severity=ValidationSeverity.MEDIUM,
        provider_scope=record.provider_code,
        agent_scope=record.agent_ref,
        source_record_id=f"{record.provider_code}-feed",
        fields=("feed_status",),
        expected=expected,
        observed=observed,
        timestamp=record.received_timestamp or record.expected_timestamp,
        usability=usability,
    )
