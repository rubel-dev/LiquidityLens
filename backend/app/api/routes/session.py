from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import SessionResponse
from app.auth.scope import AccessScope, get_access_scope
from app.persistence.database import get_db_session
from app.persistence.models.user import User

router = APIRouter(tags=["session"])
SESSION = Depends(get_db_session)
ACCESS = Depends(get_access_scope)


@router.get("/session", response_model=SessionResponse)
def get_session(
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> SessionResponse:
    user = session.scalar(select(User).where(User.id == scope.user_id))
    display_name = user.display_name if user is not None else str(scope.user_id)
    return SessionResponse(
        user_id=scope.user_id,
        display_name=display_name,
        roles=sorted(scope.roles),
        provider_ids=sorted(scope.provider_ids),
        area_ids=sorted(scope.area_ids),
        global_access=scope.global_access,
    )
