import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.persistence.models.enums import AlertPriority, AlertStatus, CaseStatus


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class EvidenceResponse(ApiModel):
    evidence_type: str
    payload: dict[str, object]


class AuditResponse(ApiModel):
    action: str
    actor_user_id: uuid.UUID | None
    previous_state: dict[str, object] | None
    new_state: dict[str, object] | None
    created_at: datetime


class AlertResponse(ApiModel):
    alert_id: uuid.UUID
    alert_type: str
    severity: AlertPriority
    provider_id: uuid.UUID | None
    agent_id: uuid.UUID
    evidence: tuple[EvidenceResponse, ...]
    confidence: Decimal
    recommended_next_step: str
    owner_user_id: uuid.UUID | None
    status: AlertStatus
    summary: str
    human_review_required: bool
    created_at: datetime
    audit_trail: tuple[AuditResponse, ...]


class AssignAlertRequest(ApiModel):
    assignee_user_id: uuid.UUID


class AcknowledgeAlertRequest(ApiModel):
    note: str | None = Field(default=None, max_length=500)


class CaseNoteResponse(ApiModel):
    note_id: uuid.UUID
    author_user_id: uuid.UUID
    body: str
    created_at: datetime


class CaseHistoryResponse(ApiModel):
    from_status: CaseStatus | None
    to_status: CaseStatus
    actor_user_id: uuid.UUID
    reason: str | None
    created_at: datetime


class EscalationResponse(ApiModel):
    escalation_id: uuid.UUID
    from_role: str
    to_role: str
    reason: str
    created_at: datetime


class CaseResponse(ApiModel):
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
    notes: tuple[CaseNoteResponse, ...]
    status_history: tuple[CaseHistoryResponse, ...]
    escalation_history: tuple[EscalationResponse, ...]
    resolution_information: str | None
    audit_event_ids: tuple[uuid.UUID, ...]


class CreateCaseRequest(ApiModel):
    alert_id: uuid.UUID
    title: str | None = Field(default=None, min_length=1, max_length=200)
    initial_note: str | None = Field(default=None, min_length=1, max_length=2000)


class EscalateCaseRequest(ApiModel):
    to_role: str = Field(min_length=1, max_length=64)
    reason: str = Field(min_length=1, max_length=500)
    expected_version: int | None = Field(default=None, ge=1)


class ResolveCaseRequest(ApiModel):
    rationale: str = Field(min_length=1, max_length=500)
    expected_version: int | None = Field(default=None, ge=1)
