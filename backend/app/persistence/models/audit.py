import uuid
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.base import Base
from app.persistence.models.mixins import CreatedAtMixin, UuidPrimaryKeyMixin


class AuditEvent(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        CheckConstraint("length(action) > 0", name="ck_audit_events_action_not_empty"),
        Index("ix_audit_entity_created", "entity_type", "entity_id", "created_at"),
        Index("ix_audit_provider_action", "provider_id", "action"),
    )

    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    provider_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    previous_state_summary: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    new_state_summary: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)


class HumanFeedback(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "human_feedback"
    __table_args__ = (Index("ix_human_feedback_case", "case_id"),)

    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    feedback_type: Mapped[str] = mapped_column(String(80), nullable=False)
    details: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)


class MetricObservation(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "metric_observations"
    __table_args__ = (
        CheckConstraint("metric_id like 'MET-%'", name="ck_metric_observations_metric_id"),
        Index("ix_metric_observations_metric_id", "metric_id"),
    )

    scenario_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scenario_runs.id"), nullable=False)
    metric_id: Mapped[str] = mapped_column(String(16), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    threshold: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    passed: Mapped[bool] = mapped_column(nullable=False)

