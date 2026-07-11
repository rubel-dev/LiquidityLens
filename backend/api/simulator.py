"""Demo scenario trigger endpoints — injects test data for live demo."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from models.agent import Agent
from data.scenarios.eid_rush import inject as inject_eid_rush
from data.scenarios.salary_day import inject as inject_salary_day
from data.scenarios.data_conflict import inject as get_data_conflict_info

router = APIRouter(prefix="/api/simulate", tags=["simulator"])


@router.post("/scenario/eid_rush")
async def trigger_eid_rush(agent_name: str = "Karim Mia", db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.name == agent_name))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    return await inject_eid_rush(str(agent.id), db)


@router.post("/scenario/salary_day")
async def trigger_salary_day(
    agent_name: str = "Karim Mia",
    provider: str = "nagad",
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Agent).where(Agent.name == agent_name))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    return await inject_salary_day(str(agent.id), provider, db)


@router.get("/scenario/data_conflict")
async def trigger_data_conflict():
    return get_data_conflict_info()
