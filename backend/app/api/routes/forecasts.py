import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import LiquidityForecastResponse
from app.auth.scope import AccessScope, get_access_scope
from app.persistence.database import get_db_session
from app.persistence.models.agent import Agent
from app.persistence.models.analytics import LiquidityForecast

router = APIRouter(tags=["forecasts"])
SESSION = Depends(get_db_session)
ACCESS = Depends(get_access_scope)


@router.get("/liquidity-forecasts", response_model=list[LiquidityForecastResponse])
def list_forecasts(
    provider_id: uuid.UUID | None = None,
    agent_id: uuid.UUID | None = None,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> list[LiquidityForecast]:
    if not scope.has_any_role("agent", "ops", "risk", "manager", "demo"):
        raise HTTPException(status_code=403, detail="insufficient role for forecast access")
    query = (
        select(LiquidityForecast)
        .join(Agent, Agent.id == LiquidityForecast.agent_id)
        .order_by(LiquidityForecast.forecast_time.desc(), LiquidityForecast.id)
    )
    if not scope.global_access:
        from sqlalchemy import false, or_

        conditions = []
        if scope.provider_ids:
            conditions.append(LiquidityForecast.provider_id.in_(scope.provider_ids))
        if scope.area_ids:
            conditions.append(Agent.area_id.in_(scope.area_ids))
        if not conditions:
            raise HTTPException(status_code=403, detail="no authorized scope for forecasts")
        query = query.where(or_(*conditions))
    if provider_id is not None:
        query = query.where(LiquidityForecast.provider_id == provider_id)
    if agent_id is not None:
        query = query.where(LiquidityForecast.agent_id == agent_id)
    return list(session.scalars(query).all())
