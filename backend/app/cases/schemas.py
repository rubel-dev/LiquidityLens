import uuid
from dataclasses import dataclass
from datetime import datetime

from app.persistence.models.enums import CaseStatus


@dataclass(frozen=True)
class CaseNoteResult:
    note_id: uuid.UUID
    author_user_id: uuid.UUID
    body: str
    created_at: datetime


@dataclass(frozen=True)
class CaseHistoryResult:
    from_status: CaseStatus | None
    to_status: CaseStatus
    actor_user_id: uuid.UUID
    reason: str | None
    created_at: datetime


@dataclass(frozen=True)
class EscalationResult:
    escalation_id: uuid.UUID
    from_role: str
    to_role: str
    reason: str
    created_at: datetime


@dataclass(frozen=True)
class CaseResult:
    case_id: uuid.UUID
    origin_alert_id: uuid.UUID | None
    provider_id: uuid.UUID | None
    agent_id: uuid.UUID
    owner_user_id: uuid.UUID | None
    status: CaseStatus
    title: str
    version: int
    created_at: datetime
    updated_at: datetime
    notes: tuple[CaseNoteResult, ...]
    status_history: tuple[CaseHistoryResult, ...]
    escalation_history: tuple[EscalationResult, ...]
    resolution_information: str | None
    audit_event_ids: tuple[uuid.UUID, ...]
