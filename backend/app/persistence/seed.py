"""Demo seed data — creates known demo users and roles for the hackathon prototype.

All users use deterministic UUIDs so the frontend can reference them by a known
X-User-ID header without a real authentication mechanism. These are synthetic
actors with no production affiliation.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.user import Role, User, UserRoleAssignment

# Deterministic demo user IDs — must match DEMO_USERS in frontend/src/lib/api.ts
DEMO_USERS = [
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "display_name": "Demo Ops User",
        "synthetic_ref": "DEMO-OPS-001",
        "role": "ops",
        "global_access": True,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000002"),
        "display_name": "Demo Field Officer",
        "synthetic_ref": "DEMO-FIELD-001",
        "role": "field",
        "global_access": True,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000003"),
        "display_name": "Demo Risk Reviewer",
        "synthetic_ref": "DEMO-RISK-001",
        "role": "risk",
        "global_access": True,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000004"),
        "display_name": "Demo Manager",
        "synthetic_ref": "DEMO-MGR-001",
        "role": "manager",
        "global_access": True,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000005"),
        "display_name": "Demo Operator",
        "synthetic_ref": "DEMO-DEMO-001",
        "role": "demo",
        "global_access": True,
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000006"),
        "display_name": "Demo Agent",
        "synthetic_ref": "DEMO-AGENT-001",
        "role": "agent",
        "global_access": True,
    },
]

VALID_ROLES = ("agent", "ops", "field", "risk", "manager", "demo")


def ensure_demo_seed(session: Session) -> None:
    """Idempotently create demo roles and users. Safe to call on every startup."""
    role_map: dict[str, uuid.UUID] = {}
    for role_name in VALID_ROLES:
        existing = session.scalar(select(Role).where(Role.name == role_name))
        if existing is None:
            role = Role(id=uuid.uuid4(), name=role_name)
            session.add(role)
            session.flush([role])
            role_map[role_name] = role.id
        else:
            role_map[role_name] = existing.id

    for spec in DEMO_USERS:
        user = session.get(User, spec["id"])
        if user is None:
            user = User(
                id=spec["id"],  # type: ignore[arg-type]
                display_name=str(spec["display_name"]),
                synthetic_user_ref=str(spec["synthetic_ref"]),
            )
            session.add(user)
            session.flush([user])

        role_id = role_map[str(spec["role"])]
        existing_assignment = session.scalar(
            select(UserRoleAssignment).where(
                UserRoleAssignment.user_id == spec["id"],  # type: ignore[arg-type]
                UserRoleAssignment.role_id == role_id,
                UserRoleAssignment.provider_id.is_(None),
                UserRoleAssignment.area_id.is_(None),
            )
        )
        if existing_assignment is None:
            session.add(
                UserRoleAssignment(
                    user_id=spec["id"],  # type: ignore[arg-type]
                    role_id=role_id,
                    provider_id=None,
                    area_id=None,
                )
            )
    session.flush()
