import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.base import Base
from app.persistence.models.mixins import UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.persistence.models.agent import Agent, AgentProviderAccount
    from app.persistence.models.scenario import ScenarioRun


class SharedCashSnapshot(UuidPrimaryKeyMixin, Base):
    __tablename__ = "shared_cash_snapshots"
    __table_args__ = (
        CheckConstraint("amount is null or amount >= 0", name="ck_shared_cash_amount_non_negative"),
        Index("ix_shared_cash_agent_observed", "agent_id", "observed_at"),
    )

    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False
    )
    amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BDT")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scenario_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenario_runs.id"),
        nullable=True,
    )

    agent: Mapped["Agent"] = relationship(back_populates="shared_cash_snapshots")
    scenario_run: Mapped["ScenarioRun | None"] = relationship(
        back_populates="shared_cash_snapshots"
    )


class ProviderBalanceSnapshot(UuidPrimaryKeyMixin, Base):
    __tablename__ = "provider_balance_snapshots"
    __table_args__ = (
        CheckConstraint(
            "amount is null or amount >= 0", name="ck_provider_balance_amount_non_negative"
        ),
        ForeignKeyConstraint(
            ["account_id", "agent_id"],
            ["agent_provider_accounts.id", "agent_provider_accounts.agent_id"],
            name="fk_provider_balance_account_agent",
        ),
        ForeignKeyConstraint(
            ["account_id", "provider_id"],
            ["agent_provider_accounts.id", "agent_provider_accounts.provider_id"],
            name="fk_provider_balance_account_provider",
        ),
        Index("ix_provider_balance_account_observed", "account_id", "observed_at"),
        Index(
            "ix_provider_balance_agent_provider_observed", "agent_id", "provider_id", "observed_at"
        ),
    )

    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False
    )
    amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BDT")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    quality_status: Mapped[str] = mapped_column(String(32), nullable=False)
    scenario_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenario_runs.id"),
        nullable=True,
    )

    account: Mapped["AgentProviderAccount"] = relationship(
        back_populates="balance_snapshots",
        foreign_keys=[account_id],
        primaryjoin="AgentProviderAccount.id == ProviderBalanceSnapshot.account_id",
    )
    scenario_run: Mapped["ScenarioRun | None"] = relationship(
        back_populates="provider_balance_snapshots"
    )
