import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.base import Base
from app.persistence.models.enums import ScenarioRunStatus, enum_values
from app.persistence.models.mixins import UuidPrimaryKeyMixin


class Scenario(UuidPrimaryKeyMixin, Base):
    __tablename__ = "scenarios"
    __table_args__ = (Index("ix_scenarios_code", "code"),)

    code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    runs: Mapped[list["ScenarioRun"]] = relationship(back_populates="scenario")


class ScenarioRun(UuidPrimaryKeyMixin, Base):
    __tablename__ = "scenario_runs"
    __table_args__ = (Index("ix_scenario_runs_scenario_status_started", "scenario_id", "status", "started_at"),)

    scenario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scenarios.id"), nullable=False)
    seed: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[ScenarioRunStatus] = mapped_column(
        Enum(ScenarioRunStatus, name="scenario_run_status", values_callable=enum_values),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    scenario: Mapped[Scenario] = relationship(back_populates="runs")
    shared_cash_snapshots: Mapped[list["SharedCashSnapshot"]] = relationship(back_populates="scenario_run")
    provider_balance_snapshots: Mapped[list["ProviderBalanceSnapshot"]] = relationship(back_populates="scenario_run")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="scenario_run")
    feed_statuses: Mapped[list["ProviderFeedStatus"]] = relationship(back_populates="scenario_run")
