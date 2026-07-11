import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, Integer, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), nullable=False)
    provider: Mapped[str | None] = mapped_column(String(20))            # None = multi-provider/cash
    type: Mapped[str] = mapped_column(String(30), nullable=False)       # liquidity|anomaly|data_quality
    severity: Mapped[str] = mapped_column(String(10), nullable=False)   # low|medium|high|critical
    message_en: Mapped[str | None] = mapped_column(Text)
    message_bn: Mapped[str | None] = mapped_column(Text)                # OpenAI-generated Bengali
    evidence: Mapped[dict | None] = mapped_column(JSONB)
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3))    # 0.000–1.000
    uncertainty: Mapped[str | None] = mapped_column(String(10))        # low|medium|high
    eta_minutes: Mapped[int | None] = mapped_column(Integer)
    owner_role: Mapped[str | None] = mapped_column(String(50))
    owner_name: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="open")    # open|acknowledged|escalated|resolved
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    agent: Mapped["Agent"] = relationship(back_populates="alerts")
    case: Mapped["Case | None"] = relationship(back_populates="alert", uselist=False)
