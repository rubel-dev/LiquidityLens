"""False positive scenario: high volume on salary day — should NOT trigger anomaly."""
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from models.transaction import Transaction
from data.synthetic import generate_salary_day_spike


async def inject(agent_id: str, provider: str, db: AsyncSession) -> dict:
    for t in generate_salary_day_spike(agent_id, provider):
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
    return {"scenario": "salary_day", "agent_id": agent_id, "provider": provider, "status": "injected"}
