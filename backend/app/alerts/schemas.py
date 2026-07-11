import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from app.persistence.models.enums import AlertPriority, AlertStatus


class AlertType(StrEnum):
    LIQUIDITY_SHORTAGE = "liquidity_shortage"
    ANOMALY_FINDING = "anomaly_finding"
    DATA_QUALITY = "data_quality"


@dataclass(frozen=True)
class AlertEvidence:
    evidence_type: str
    payload: dict[str, object]


@dataclass(frozen=True)
class AlertAudit:
    action: str
    actor_user_id: uuid.UUID | None
    previous_state: dict[str, object] | None
    new_state: dict[str, object] | None
    created_at: datetime


@dataclass(frozen=True)
class AlertResult:
    alert_id: uuid.UUID
    alert_type: str
    severity: AlertPriority
    provider_id: uuid.UUID | None
    agent_id: uuid.UUID
    evidence: tuple[AlertEvidence, ...]
    confidence: Decimal
    recommended_next_step: str
    owner_user_id: uuid.UUID | None
    status: AlertStatus
    summary: str
    human_review_required: bool
    created_at: datetime
    audit_trail: tuple[AlertAudit, ...]
