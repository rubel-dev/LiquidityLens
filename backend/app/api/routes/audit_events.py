import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import AuditEventResponse
from app.auth.scope import AccessScope, get_access_scope
from app.persistence.database import get_db_session
from app.persistence.models.audit import AuditEvent

router = APIRouter(tags=["audit"])
SESSION = Depends(get_db_session)
ACCESS = Depends(get_access_scope)


@router.get("/audit-events", response_model=list[AuditEventResponse])
def list_audit_events(
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    provider_id: uuid.UUID | None = None,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> list[AuditEvent]:
    if not scope.has_any_role("ops", "risk", "manager", "demo"):
        raise HTTPException(status_code=403, detail="ops, risk, or manager role required")
    query = select(AuditEvent).order_by(AuditEvent.created_at.desc(), AuditEvent.id)
    if not scope.global_access:
        from sqlalchemy import false, or_

        conditions = [AuditEvent.provider_id.is_(None)]
        if scope.provider_ids:
            conditions.append(AuditEvent.provider_id.in_(scope.provider_ids))
        query = query.where(or_(*conditions))
    if entity_type is not None:
        query = query.where(AuditEvent.entity_type == entity_type)
    if entity_id is not None:
        query = query.where(AuditEvent.entity_id == entity_id)
    if provider_id is not None:
        query = query.where(AuditEvent.provider_id == provider_id)
    return list(session.scalars(query.limit(200)).all())
