"""Scenario A+B: Hidden bKash shortage + anomalous velocity simultaneously."""
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from models.balance import ProviderBalance
from models.transaction import Transaction
from data.synthetic import generate_anomaly_velocity


async def inject(agent_id: str, db: AsyncSession) -> dict:
    # Drive bKash balance to critically low
    result = await db.execute(
        select(ProviderBalance).where(
            and_(
                ProviderBalance.agent_id == agent_id,
                ProviderBalance.provider == "bkash",
            )
        ).order_by(ProviderBalance.fetched_at.desc()).limit(1)
    )
    row = result.scalar_one_or_none()
    if row:
        row.balance = 1200.0
        row.data_quality = "ok"
        row.fetched_at = datetime.now(timezone.utc)

    # Inject anomaly transactions
    for t in generate_anomaly_velocity(agent_id, "bkash"):
        db.add(Transaction(
            id=uuid.UUID(t["id"]),
            agent_id=uuid.UUID(agent_id),
            provider=t["provider"],
            type=t["type"],
            amount=t["amount"],
            account_id=t["account_id"],
            timestamp=t["timestamp"],
            status=t["status"],
        ))

    await db.commit()
    return {"scenario": "eid_rush", "agent_id": agent_id, "status": "injected"}
