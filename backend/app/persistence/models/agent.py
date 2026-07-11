import uuid

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.base import Base
from app.persistence.models.enums import AccountStatus, AgentStatus, enum_values
from app.persistence.models.mixins import CreatedAtMixin, UuidPrimaryKeyMixin


class Agent(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "agents"
    __table_args__ = (
        CheckConstraint("synthetic_agent_ref not like '+880%'", name="ck_agents_no_phone_ref"),
        Index("ix_agents_area", "area_id"),
    )

    area_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("areas.id"), nullable=False)
    synthetic_agent_ref: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    display_code: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[AgentStatus] = mapped_column(
        Enum(AgentStatus, name="agent_status", values_callable=enum_values),
        nullable=False,
    )

    area: Mapped["Area"] = relationship(back_populates="agents")
    accounts: Mapped[list["AgentProviderAccount"]] = relationship(back_populates="agent")
    shared_cash_snapshots: Mapped[list["SharedCashSnapshot"]] = relationship(back_populates="agent")


class AgentProviderAccount(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "agent_provider_accounts"
    __table_args__ = (
        UniqueConstraint("agent_id", "provider_id", name="uq_agent_provider_account"),
        UniqueConstraint("synthetic_account_ref", name="uq_agent_provider_synthetic_ref"),
        UniqueConstraint("id", "agent_id", name="uq_agent_provider_account_id_agent"),
        UniqueConstraint("id", "provider_id", name="uq_agent_provider_account_id_provider"),
        CheckConstraint("synthetic_account_ref not like '+880%'", name="ck_accounts_no_phone_ref"),
        Index("ix_agent_provider_accounts_provider_agent", "provider_id", "agent_id"),
    )

    agent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
    synthetic_account_ref: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus, name="account_status", values_callable=enum_values),
        nullable=False,
    )

    agent: Mapped[Agent] = relationship(back_populates="accounts")
    provider: Mapped["Provider"] = relationship(back_populates="accounts")
    balance_snapshots: Mapped[list["ProviderBalanceSnapshot"]] = relationship(
        back_populates="account",
        foreign_keys="ProviderBalanceSnapshot.account_id",
        primaryjoin="AgentProviderAccount.id == ProviderBalanceSnapshot.account_id",
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="account",
        foreign_keys="Transaction.account_id",
        primaryjoin="AgentProviderAccount.id == Transaction.account_id",
    )
