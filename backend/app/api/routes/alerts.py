import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.alerts.exceptions import (
    AlertAuthorizationError,
    AlertConflictError,
    AlertNotFoundError,
)
from app.alerts.service import AlertService
from app.api.schemas import (
    AcknowledgeAlertRequest,
    AlertResponse,
    AssignAlertRequest,
)
from app.auth.scope import AccessScope, get_access_scope
from app.persistence.database import get_db_session
from app.persistence.models.enums import AlertPriority, AlertStatus

router = APIRouter(prefix="/alerts", tags=["alerts"])
SESSION = Depends(get_db_session)
ACCESS = Depends(get_access_scope)


@router.get("", response_model=list[AlertResponse])
def list_alerts(
    provider_id: uuid.UUID | None = None,
    status: AlertStatus | None = None,
    severity: AlertPriority | None = None,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> tuple[object, ...]:
    return AlertService(session).list_alerts(
        scope, provider_id=provider_id, status=status, severity=severity
    )


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: uuid.UUID,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> object:
    try:
        return AlertService(session).get_alert(alert_id, scope)
    except AlertNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: uuid.UUID,
    payload: AcknowledgeAlertRequest,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> object:
    try:
        return AlertService(session).acknowledge(alert_id, scope, payload.note)
    except AlertNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AlertAuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except AlertConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{alert_id}/assign", response_model=AlertResponse)
def assign_alert(
    alert_id: uuid.UUID,
    payload: AssignAlertRequest,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> object:
    try:
        return AlertService(session).assign(alert_id, payload.assignee_user_id, scope)
    except AlertNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AlertAuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except AlertConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
