import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.persistence.models.enums import AlertPriority, AlertStatus, CaseStatus


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ── Session ──────────────────────────────────────────────────────────────────


class SessionResponse(BaseModel):
    user_id: uuid.UUID
    display_name: str
    roles: list[str]
    provider_ids: list[uuid.UUID]
    area_ids: list[uuid.UUID]
    global_access: bool


# ── Scenarios ────────────────────────────────────────────────────────────────


class ScenarioSummaryResponse(ApiModel):
    scenario_id: uuid.UUID = Field(alias="id")
    code: str
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RunScenarioRequest(BaseModel):
    seed: int | str = Field(default=5001)
    profile: str = Field(default="demo")


class ScenarioRunResponse(BaseModel):
    run_ref: str
    scenario_code: str
    status: str
    seed: str
    fingerprint: str
    generated_counts: dict[str, int]


# ── Liquidity Forecasts ───────────────────────────────────────────────────────


class LiquidityForecastResponse(ApiModel):
    forecast_id: uuid.UUID = Field(alias="id")
    agent_id: uuid.UUID
    provider_id: uuid.UUID | None
    forecast_type: str
    forecast_time: datetime
    shortage_at: datetime | None
    confidence: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ── Anomaly Findings ──────────────────────────────────────────────────────────


class AnomalyFindingResponse(ApiModel):
    finding_id: uuid.UUID = Field(alias="id")
    provider_id: uuid.UUID
    agent_id: uuid.UUID
    finding_type: str
    severity: str
    score: Decimal
    detected_at: datetime
    human_review_required: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ── Data Quality ──────────────────────────────────────────────────────────────


class DataQualityStatusResponse(ApiModel):
    status_id: uuid.UUID = Field(alias="id")
    provider_id: uuid.UUID
    agent_id: uuid.UUID | None
    status: str
    observed_at: datetime
    ingested_at: datetime | None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ── Audit Events ──────────────────────────────────────────────────────────────


class AuditEventResponse(ApiModel):
    event_id: uuid.UUID = Field(alias="id")
    action: str
    entity_type: str
    entity_id: uuid.UUID
    actor_user_id: uuid.UUID | None
    provider_id: uuid.UUID | None
    previous_state: dict[str, object] | None = Field(alias="previous_state_summary")
    new_state: dict[str, object] | None = Field(alias="new_state_summary")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ── Case Notes ────────────────────────────────────────────────────────────────


class CreateCaseNoteRequest(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


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
