import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import AnomalyFindingResponse
from app.auth.scope import AccessScope, get_access_scope
from app.persistence.database import get_db_session
from app.persistence.models.agent import Agent
from app.persistence.models.analytics import AnomalyFinding

router = APIRouter(tags=["findings"])
SESSION = Depends(get_db_session)
ACCESS = Depends(get_access_scope)


@router.get("/anomaly-findings", response_model=list[AnomalyFindingResponse])
def list_findings(
    provider_id: uuid.UUID | None = None,
    agent_id: uuid.UUID | None = None,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> list[AnomalyFinding]:
    if not scope.has_any_role("ops", "risk", "manager", "demo"):
        raise HTTPException(status_code=403, detail="ops, risk, or manager role required")
    query = (
        select(AnomalyFinding)
        .join(Agent, Agent.id == AnomalyFinding.agent_id)
        .order_by(AnomalyFinding.detected_at.desc(), AnomalyFinding.id)
    )
    if not scope.global_access:
        from sqlalchemy import false, or_

        conditions = []
        if scope.provider_ids:
            conditions.append(AnomalyFinding.provider_id.in_(scope.provider_ids))
        if scope.area_ids:
            conditions.append(Agent.area_id.in_(scope.area_ids))
        if not conditions:
            raise HTTPException(status_code=403, detail="no authorized scope for findings")
        query = query.where(or_(*conditions))
    if provider_id is not None:
        query = query.where(AnomalyFinding.provider_id == provider_id)
    if agent_id is not None:
        query = query.where(AnomalyFinding.agent_id == agent_id)
    return list(session.scalars(query).all())
