import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.base import Base
from app.persistence.models.enums import CaseStatus, enum_values
from app.persistence.models.mixins import CreatedAtMixin, UpdatedAtMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.persistence.models.alert import Alert


class Case(UuidPrimaryKeyMixin, UpdatedAtMixin, Base):
    __tablename__ = "cases"
    __table_args__ = (
        CheckConstraint("version >= 1", name="ck_cases_version_positive"),
        UniqueConstraint("origin_alert_id", name="uq_cases_origin_alert"),
        Index(
            "ix_cases_status_owner_provider_updated",
            "status",
            "owner_user_id",
            "provider_id",
            "updated_at",
        ),
    )

    origin_alert_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=True
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
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus, name="case_status", values_callable=enum_values),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[int] = mapped_column(nullable=False, default=1)

    origin_alert: Mapped["Alert | None"] = relationship(back_populates="origin_case")
    notes: Mapped[list["CaseNote"]] = relationship(back_populates="case")
    status_history: Mapped[list["CaseStatusHistory"]] = relationship(back_populates="case")
    escalations: Mapped[list["Escalation"]] = relationship(back_populates="case")


class CaseNote(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "case_notes"
    __table_args__ = (
        CheckConstraint("length(note) > 0", name="ck_case_notes_not_empty"),
        Index("ix_case_notes_case", "case_id"),
    )

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False
    )
    author_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    note: Mapped[str] = mapped_column(String(2000), nullable=False)

    case: Mapped[Case] = relationship(back_populates="notes")


class CaseStatusHistory(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "case_status_history"
    __table_args__ = (Index("ix_case_status_history_case_created", "case_id", "created_at"),)

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False
    )
    from_status: Mapped[CaseStatus | None] = mapped_column(
        Enum(CaseStatus, name="case_status", values_callable=enum_values),
        nullable=True,
    )
    to_status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus, name="case_status", values_callable=enum_values),
        nullable=False,
    )
    actor_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    case: Mapped[Case] = relationship(back_populates="status_history")


class Escalation(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "escalations"
    __table_args__ = (
        CheckConstraint("length(reason) > 0", name="ck_escalations_reason_not_empty"),
        Index("ix_escalations_case", "case_id"),
    )

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False
    )
    from_role: Mapped[str] = mapped_column(String(64), nullable=False)
    to_role: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)

    case: Mapped[Case] = relationship(back_populates="escalations")
