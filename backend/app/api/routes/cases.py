import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import (
    CaseNoteResponse,
    CaseResponse,
    CreateCaseNoteRequest,
    CreateCaseRequest,
    EscalateCaseRequest,
    ResolveCaseRequest,
)
from app.auth.scope import AccessScope, get_access_scope
from app.cases.exceptions import (
    CaseAuthorizationError,
    CaseConflictError,
    CaseNotFoundError,
)
from app.cases.service import CaseService
from app.persistence.database import get_db_session
from app.persistence.models.enums import CaseStatus

router = APIRouter(prefix="/cases", tags=["cases"])
SESSION = Depends(get_db_session)
ACCESS = Depends(get_access_scope)


@router.get("", response_model=list[CaseResponse])
def list_cases(
    provider_id: uuid.UUID | None = None,
    status: CaseStatus | None = None,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> tuple[object, ...]:
    return CaseService(session).list_cases(scope, provider_id=provider_id, status=status)


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(
    case_id: uuid.UUID,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> object:
    try:
        return CaseService(session).get_case(case_id, scope)
    except CaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=CaseResponse, status_code=201)
def create_case(
    payload: CreateCaseRequest,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> object:
    try:
        return CaseService(session).create_from_alert(
            payload.alert_id,
            scope,
            title=payload.title,
            initial_note=payload.initial_note,
        )
    except CaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CaseAuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except CaseConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{case_id}/notes", response_model=CaseNoteResponse, status_code=201)
def add_case_note(
    case_id: uuid.UUID,
    payload: CreateCaseNoteRequest,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> object:
    try:
        result = CaseService(session).add_note(case_id, scope, payload.body)
        latest = result.notes[-1] if result.notes else None
        if latest is None:
            raise HTTPException(status_code=500, detail="note was not persisted")
        return latest
    except CaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CaseAuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except CaseConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{case_id}/escalate", response_model=CaseResponse)
def escalate_case(
    case_id: uuid.UUID,
    payload: EscalateCaseRequest,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> object:
    try:
        return CaseService(session).escalate(
            case_id,
            scope,
            to_role=payload.to_role,
            reason=payload.reason,
            expected_version=payload.expected_version,
        )
    except CaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CaseAuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except CaseConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{case_id}/resolve", response_model=CaseResponse)
def resolve_case(
    case_id: uuid.UUID,
    payload: ResolveCaseRequest,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> object:
    try:
        return CaseService(session).resolve(
            case_id,
            scope,
            rationale=payload.rationale,
            expected_version=payload.expected_version,
        )
    except CaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CaseAuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except CaseConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
