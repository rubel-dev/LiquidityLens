from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from models.agent import Agent
from models.balance import ProviderBalance
from models.alert import Alert

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("")
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.status == "active").order_by(Agent.name))
    agents = result.scalars().all()
    out = []
    for agent in agents:
        # latest balances
        bal_result = await db.execute(
            select(ProviderBalance)
            .where(ProviderBalance.agent_id == agent.id)
            .order_by(ProviderBalance.fetched_at.desc())
        )
        balances = bal_result.scalars().all()
        # deduplicate — keep latest per provider
        seen = {}
        for b in balances:
            if b.provider not in seen:
                seen[b.provider] = b

        total_emoney = sum(
            float(b.balance) for b in seen.values() if b.balance is not None
        )
        open_alerts = await db.execute(
            select(Alert).where(
                Alert.agent_id == agent.id,
                Alert.status.in_(["open", "acknowledged", "escalated"]),
            )
        )
        alert_count = len(open_alerts.scalars().all())

        out.append({
            "id": str(agent.id),
            "name": agent.name,
            "area": agent.area,
            "physical_cash": float(agent.physical_cash),
            "total_emoney": round(total_emoney, 2),
            "total_balance": round(float(agent.physical_cash) + total_emoney, 2),
            "open_alerts": alert_count,
            "status": agent.status,
            "providers": {b.provider: {
                "balance": float(b.balance) if b.balance else None,
                "data_quality": b.data_quality,
            } for b in seen.values()},
        })
    return out


@router.get("/{agent_id}")
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    bal_result = await db.execute(
        select(ProviderBalance)
        .where(ProviderBalance.agent_id == agent.id)
        .order_by(ProviderBalance.fetched_at.desc())
    )
    balances = bal_result.scalars().all()
    seen = {}
    for b in balances:
        if b.provider not in seen:
            seen[b.provider] = b

    return {
        "id": str(agent.id),
        "name": agent.name,
        "area": agent.area,
        "phone": agent.phone,
        "physical_cash": float(agent.physical_cash),
        "status": agent.status,
        "providers": {b.provider: {
            "balance": float(b.balance) if b.balance else None,
            "data_quality": b.data_quality,
            "fetched_at": b.fetched_at.isoformat(),
            "latency_ms": b.latency_ms,
        } for b in seen.values()},
    }
