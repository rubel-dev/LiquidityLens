import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.base import Base
from app.persistence.models.enums import FeedQualityStatus, Severity, enum_values
from app.persistence.models.mixins import CreatedAtMixin, UuidPrimaryKeyMixin


class ProviderFeedStatus(UuidPrimaryKeyMixin, Base):
    __tablename__ = "provider_feed_statuses"
    __table_args__ = (
        Index("ix_feed_provider_agent_observed", "provider_id", "agent_id", "observed_at"),
        Index("ix_feed_provider_status", "provider_id", "status"),
    )

    provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
    agent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    scenario_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenario_runs.id"),
        nullable=True,
    )
    status: Mapped[FeedQualityStatus] = mapped_column(
        Enum(FeedQualityStatus, name="feed_quality_status", values_callable=enum_values),
        nullable=False,
    )
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ingested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    provider: Mapped["Provider"] = relationship(back_populates="feed_statuses")
    scenario_run: Mapped["ScenarioRun | None"] = relationship(back_populates="feed_statuses")
    quality_events: Mapped[list["DataQualityEvent"]] = relationship(back_populates="feed_status")


class DataQualityEvent(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "data_quality_events"
    __table_args__ = (Index("ix_data_quality_event_type", "event_type"),)

    feed_status_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("provider_feed_statuses.id"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity, name="severity", values_callable=enum_values),
        nullable=False,
    )
    details: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)

    feed_status: Mapped[ProviderFeedStatus] = relationship(back_populates="quality_events")
