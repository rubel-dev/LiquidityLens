import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import DataQualityStatusResponse
from app.auth.scope import AccessScope, get_access_scope
from app.persistence.database import get_db_session
from app.persistence.models.feed import ProviderFeedStatus

router = APIRouter(tags=["data-quality"])
SESSION = Depends(get_db_session)
ACCESS = Depends(get_access_scope)


@router.get("/data-quality-statuses", response_model=list[DataQualityStatusResponse])
def list_data_quality_statuses(
    provider_id: uuid.UUID | None = None,
    run_id: uuid.UUID | None = None,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> list[ProviderFeedStatus]:
    if not scope.has_any_role("ops", "risk", "manager", "demo"):
        raise HTTPException(status_code=403, detail="ops, risk, or manager role required")
    query = select(ProviderFeedStatus).order_by(
        ProviderFeedStatus.observed_at.desc(), ProviderFeedStatus.id
    )
    if not scope.global_access:
        from sqlalchemy import false, or_

        conditions = []
        if scope.provider_ids:
            conditions.append(ProviderFeedStatus.provider_id.in_(scope.provider_ids))
        if not conditions:
            raise HTTPException(status_code=403, detail="no authorized scope for feed statuses")
        query = query.where(or_(*conditions))
    if provider_id is not None:
        query = query.where(ProviderFeedStatus.provider_id == provider_id)
    if run_id is not None:
        query = query.where(ProviderFeedStatus.scenario_run_id == run_id)
    return list(session.scalars(query).all())
