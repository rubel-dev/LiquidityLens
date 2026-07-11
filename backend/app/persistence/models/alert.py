import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.base import Base
from app.persistence.models.enums import (
    AlertPriority,
    AlertStatus,
    ExplanationLanguage,
    ReviewStatus,
    enum_values,
)
from app.persistence.models.mixins import CreatedAtMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.persistence.models.case import Case


class Alert(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "alerts"
    __table_args__ = (
        Index(
            "ix_alerts_status_priority_owner_provider_created",
            "status",
            "priority",
            "owner_user_id",
            "provider_id",
            "created_at",
        ),
    )

    provider_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("providers.id"), nullable=True
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False
    )
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    alert_type: Mapped[str] = mapped_column(String(80), nullable=False)
    priority: Mapped[AlertPriority] = mapped_column(
        Enum(AlertPriority, name="alert_priority", values_callable=enum_values),
        nullable=False,
    )
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, name="alert_status", values_callable=enum_values),
        nullable=False,
    )
    review_status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, name="review_status", values_callable=enum_values),
        nullable=False,
    )
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    recommended_next_step: Mapped[str | None] = mapped_column(String(500), nullable=True)
    human_review_required: Mapped[bool] = mapped_column(nullable=False, default=True)

    assignments: Mapped[list["AlertAssignment"]] = relationship(back_populates="alert")
    explanations: Mapped[list["ExplanationRecord"]] = relationship(back_populates="alert")
    origin_case: Mapped["Case | None"] = relationship(back_populates="origin_alert")


class AlertAssignment(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "alert_assignments"
    __table_args__ = (Index("ix_alert_assignments_alert", "alert_id"),)

    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=False
    )
    assigned_to_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    assigned_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    alert: Mapped[Alert] = relationship(back_populates="assignments")


class ExplanationRecord(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "explanation_records"
    __table_args__ = (Index("ix_explanation_alert", "alert_id"),)

    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=False
    )
    language: Mapped[ExplanationLanguage] = mapped_column(
        Enum(ExplanationLanguage, name="explanation_language", values_callable=enum_values),
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    explanation_text: Mapped[str] = mapped_column(String(2000), nullable=False)
    fallback_used: Mapped[bool] = mapped_column(nullable=False, default=True)

    alert: Mapped[Alert] = relationship(back_populates="explanations")
