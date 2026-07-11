import uuid
from dataclasses import dataclass

from fastapi import Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.database import SessionLocal
from app.persistence.models.user import Role, User, UserRoleAssignment


@dataclass(frozen=True)
class AccessScope:
    user_id: uuid.UUID
    roles: frozenset[str]
    provider_ids: frozenset[uuid.UUID]
    area_ids: frozenset[uuid.UUID]
    global_access: bool = False

    def has_any_role(self, *roles: str) -> bool:
        return bool(self.roles.intersection(roles))


def load_access_scope(session: Session, user_id: uuid.UUID) -> AccessScope:
    if session.get(User, user_id) is None:
        raise HTTPException(status_code=401, detail="unknown user")
    assignments = session.execute(
        select(UserRoleAssignment, Role.name)
        .join(Role, Role.id == UserRoleAssignment.role_id)
        .where(UserRoleAssignment.user_id == user_id)
    ).all()
    if not assignments:
        raise HTTPException(status_code=403, detail="user has no authorized scope")
    return AccessScope(
        user_id=user_id,
        roles=frozenset(role_name for _assignment, role_name in assignments),
        provider_ids=frozenset(
            assignment.provider_id
            for assignment, _role_name in assignments
            if assignment.provider_id is not None
        ),
        area_ids=frozenset(
            assignment.area_id
            for assignment, _role_name in assignments
            if assignment.area_id is not None
        ),
        global_access=any(
            assignment.provider_id is None and assignment.area_id is None
            for assignment, _role_name in assignments
        ),
    )


def get_access_scope(
    x_user_id: str | None = Header(default=None, alias="X-User-ID"),
) -> AccessScope:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-ID header is required")
    try:
        user_id = uuid.UUID(x_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="X-User-ID must be a UUID") from exc
    with SessionLocal() as session:
        return load_access_scope(session, user_id)
