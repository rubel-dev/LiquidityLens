import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.base import Base
from app.persistence.models.enums import TransactionStatus, TransactionType, enum_values
from app.persistence.models.mixins import UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.persistence.models.agent import AgentProviderAccount
    from app.persistence.models.scenario import ScenarioRun


class Transaction(UuidPrimaryKeyMixin, Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        CheckConstraint(
            "synthetic_customer_ref not like '+880%'", name="ck_transactions_no_phone_customer"
        ),
        ForeignKeyConstraint(
            ["account_id", "agent_id"],
            ["agent_provider_accounts.id", "agent_provider_accounts.agent_id"],
            name="fk_transactions_account_agent",
        ),
        ForeignKeyConstraint(
            ["account_id", "provider_id"],
            ["agent_provider_accounts.id", "agent_provider_accounts.provider_id"],
            name="fk_transactions_account_provider",
        ),
        Index("ix_transactions_agent_occurred", "agent_id", "occurred_at"),
        Index("ix_transactions_provider_occurred", "provider_id", "occurred_at"),
        Index("ix_transactions_account_occurred", "synthetic_account_ref", "occurred_at"),
    )

    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False
    )
    synthetic_transaction_ref: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    synthetic_account_ref: Mapped[str] = mapped_column(String(40), nullable=False)
    synthetic_customer_ref: Mapped[str] = mapped_column(String(40), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, name="transaction_type", values_callable=enum_values),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BDT")
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus, name="transaction_status", values_callable=enum_values),
        nullable=False,
    )
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scenario_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenario_runs.id"),
        nullable=True,
    )

    account: Mapped["AgentProviderAccount"] = relationship(
        back_populates="transactions",
        foreign_keys=[account_id],
        primaryjoin="AgentProviderAccount.id == Transaction.account_id",
    )
    scenario_run: Mapped["ScenarioRun | None"] = relationship(back_populates="transactions")
