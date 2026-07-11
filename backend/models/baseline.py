import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class TransactionBaseline(Base):
    __tablename__ = "transaction_baselines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    hour_of_day: Mapped[int] = mapped_column(Integer)                  # 0–23
    day_type: Mapped[str] = mapped_column(String(20))                  # weekday|weekend|eid|salary_day
    avg_count: Mapped[float] = mapped_column(Numeric(8, 2), default=0)
    avg_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    stddev: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
