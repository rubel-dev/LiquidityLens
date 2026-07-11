import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    physical_cash: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    balances: Mapped[list["ProviderBalance"]] = relationship(
        back_populates="agent", lazy="select"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="agent", lazy="select"
    )
    alerts: Mapped[list["Alert"]] = relationship(
        back_populates="agent", lazy="select"
    )
