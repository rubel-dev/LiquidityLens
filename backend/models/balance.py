import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base


class ProviderBalance(Base):
    __tablename__ = "provider_balances"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)   # bkash|nagad|rocket
    balance: Mapped[float | None] = mapped_column(Numeric(12, 2))
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    data_quality: Mapped[str] = mapped_column(
        String(20), default="ok"                                         # ok|delayed|missing|conflict
    )
    latency_ms: Mapped[int | None] = mapped_column(Integer)

    agent: Mapped["Agent"] = relationship(back_populates="balances")
