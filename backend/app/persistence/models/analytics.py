import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.base import Base
from app.persistence.models.mixins import CreatedAtMixin, UuidPrimaryKeyMixin


class RuleVersion(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "rule_versions"
    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_rule_versions_name_version"),
        Index("ix_rule_versions_name_active", "name", "active"),
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    version: Mapped[str] = mapped_column(String(40), nullable=False)
    config: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    active: Mapped[bool] = mapped_column(nullable=False, default=True)


class LiquidityForecast(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "liquidity_forecasts"
    __table_args__ = (
        CheckConstraint(
            "confidence >= 0 and confidence <= 1", name="ck_forecasts_confidence_range"
        ),
        Index("ix_forecasts_agent_provider_time", "agent_id", "provider_id", "forecast_time"),
    )

    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False
    )
    provider_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("providers.id"), nullable=True
    )
    forecast_type: Mapped[str] = mapped_column(String(64), nullable=False)
    forecast_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    shortage_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)


class AnomalyFinding(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "anomaly_findings"
    __table_args__ = (
        CheckConstraint("score >= 0", name="ck_anomaly_score_non_negative"),
        Index("ix_anomaly_agent_provider_detected", "agent_id", "provider_id", "detected_at"),
    )

    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False
    )
    rule_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rule_versions.id"), nullable=False
    )
    finding_type: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    human_review_required: Mapped[bool] = mapped_column(nullable=False, default=True)


class ConfidenceAssessment(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "confidence_assessments"
    __table_args__ = (
        CheckConstraint(
            "confidence >= 0 and confidence <= 1", name="ck_confidence_assessments_range"
        ),
        Index("ix_confidence_subject", "subject_type", "subject_id"),
    )

    subject_type: Mapped[str] = mapped_column(String(64), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    reasons: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)


class EvidenceItem(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "evidence_items"
    __table_args__ = (
        CheckConstraint(
            "alert_id is not null or forecast_id is not null or finding_id is not null",
            name="ck_evidence_has_parent",
        ),
        Index("ix_evidence_alert", "alert_id"),
    )

    alert_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=True
    )
    forecast_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("liquidity_forecasts.id"),
        nullable=True,
    )
    finding_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("anomaly_findings.id"),
        nullable=True,
    )
    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
