import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import Select, false, or_, select
from sqlalchemy.orm import Session

from app.alerts.exceptions import (
    AlertAuthorizationError,
    AlertNotFoundError,
    AlertSourceError,
)
from app.alerts.schemas import AlertAudit, AlertEvidence, AlertResult
from app.auth.scope import AccessScope, load_access_scope
from app.persistence.models.agent import Agent
from app.persistence.models.alert import Alert, AlertAssignment
from app.persistence.models.analytics import (
    AnomalyFinding,
    ConfidenceAssessment,
    EvidenceItem,
    LiquidityForecast,
)
from app.persistence.models.audit import AuditEvent
from app.persistence.models.enums import AlertPriority, AlertStatus, ReviewStatus
from app.persistence.models.feed import ProviderFeedStatus


class AlertRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_alerts(
        self,
        scope: AccessScope,
        *,
        provider_id: uuid.UUID | None = None,
        status: AlertStatus | None = None,
        severity: AlertPriority | None = None,
    ) -> tuple[AlertResult, ...]:
        query = self._scope_query(scope)
        if provider_id is not None:
            query = query.where(Alert.provider_id == provider_id)
        if status is not None:
            query = query.where(Alert.status == status)
        if severity is not None:
            query = query.where(Alert.priority == severity)
        rows = self.session.scalars(query.order_by(Alert.created_at.desc(), Alert.id)).all()
        return tuple(self.to_result(row) for row in rows)

    def require_alert(self, alert_id: uuid.UUID, scope: AccessScope) -> Alert:
        alert = self.session.scalar(self._scope_query(scope).where(Alert.id == alert_id))
        if alert is None:
            raise AlertNotFoundError("alert not found in authorized scope")
        return alert

    def require_assignee_scope(self, user_id: uuid.UUID, alert: Alert) -> None:
        target = load_access_scope(self.session, user_id)
        agent = self.session.get(Agent, alert.agent_id)
        area_id = None if agent is None else agent.area_id
        if not (
            target.global_access
            or (alert.provider_id is not None and alert.provider_id in target.provider_ids)
            or (area_id is not None and area_id in target.area_ids)
        ):
            raise AlertAuthorizationError("assignee is outside the alert scope")

    def find_source_alert(self, source_type: str, source_id: uuid.UUID) -> Alert | None:
        return self.session.scalar(
            select(Alert)
            .join(EvidenceItem, EvidenceItem.alert_id == Alert.id)
            .where(
                EvidenceItem.evidence_type == "alert_source",
                EvidenceItem.payload["source_type"].astext == source_type,
                EvidenceItem.payload["source_id"].astext == str(source_id),
            )
        )

    def require_forecast(self, source_id: uuid.UUID) -> LiquidityForecast:
        row = self.session.get(LiquidityForecast, source_id)
        if row is None:
            raise AlertNotFoundError("liquidity forecast not found")
        return row

    def require_finding(self, source_id: uuid.UUID) -> AnomalyFinding:
        row = self.session.get(AnomalyFinding, source_id)
        if row is None:
            raise AlertNotFoundError("anomaly finding not found")
        return row

    def require_feed_status(self, source_id: uuid.UUID) -> ProviderFeedStatus:
        row = self.session.get(ProviderFeedStatus, source_id)
        if row is None:
            raise AlertNotFoundError("feed status not found")
        if row.agent_id is None:
            raise AlertSourceError("feed status has no agent scope")
        return row

    def source_evidence(
        self, *, forecast_id: uuid.UUID | None = None, finding_id: uuid.UUID | None = None
    ) -> tuple[AlertEvidence, ...]:
        query = select(EvidenceItem)
        if forecast_id is not None:
            query = query.where(EvidenceItem.forecast_id == forecast_id)
        elif finding_id is not None:
            query = query.where(EvidenceItem.finding_id == finding_id)
        else:
            return ()
        rows = self.session.scalars(query.order_by(EvidenceItem.created_at, EvidenceItem.id)).all()
        return tuple(AlertEvidence(row.evidence_type, row.payload) for row in rows)

    def source_confidence(self, subject_type: str, subject_id: uuid.UUID) -> Decimal:
        value = self.session.scalar(
            select(ConfidenceAssessment.confidence)
            .where(
                ConfidenceAssessment.subject_type == subject_type,
                ConfidenceAssessment.subject_id == subject_id,
            )
            .order_by(ConfidenceAssessment.created_at.desc())
        )
        return Decimal("0") if value is None else Decimal(value)

    def create(
        self,
        *,
        alert_type: str,
        priority: AlertPriority,
        provider_id: uuid.UUID | None,
        agent_id: uuid.UUID,
        summary: str,
        next_step: str,
        confidence: Decimal,
        source_type: str,
        source_id: uuid.UUID,
        evidence: tuple[AlertEvidence, ...],
    ) -> Alert:
        alert = Alert(
            id=uuid.uuid4(),
            provider_id=provider_id,
            agent_id=agent_id,
            alert_type=alert_type,
            priority=priority,
            status=AlertStatus.OPEN,
            review_status=ReviewStatus.NEEDS_REVIEW,
            summary=summary,
            recommended_next_step=next_step,
            human_review_required=True,
            created_at=datetime.now(UTC),
        )
        self.session.add(alert)
        self.session.flush([alert])
        self.session.add(
            EvidenceItem(
                alert_id=alert.id,
                evidence_type="alert_source",
                payload={"source_type": source_type, "source_id": str(source_id)},
            )
        )
        self.session.add_all(
            EvidenceItem(
                alert_id=alert.id,
                evidence_type=item.evidence_type,
                payload=item.payload,
            )
            for item in evidence
        )
        self.session.add(
            ConfidenceAssessment(
                subject_type="alert",
                subject_id=alert.id,
                confidence=confidence,
                reasons={
                    "source_type": source_type,
                    "source_id": str(source_id),
                    "human_review_required": True,
                    "advisory_only": True,
                },
            )
        )
        self.audit(
            alert,
            action="alert.created",
            actor_user_id=None,
            previous=None,
            new={"status": AlertStatus.OPEN.value, "owner_user_id": None},
        )
        return alert

    def assign(self, alert: Alert, *, assignee_id: uuid.UUID, actor_id: uuid.UUID) -> None:
        previous = self._state(alert)
        alert.owner_user_id = assignee_id
        self.session.add(
            AlertAssignment(
                alert_id=alert.id,
                assigned_to_user_id=assignee_id,
                assigned_by_user_id=actor_id,
                created_at=datetime.now(UTC),
            )
        )
        self.audit(
            alert,
            action="alert.assigned",
            actor_user_id=actor_id,
            previous=previous,
            new=self._state(alert),
        )

    def change_status(
        self,
        alert: Alert,
        *,
        status: AlertStatus,
        actor_id: uuid.UUID,
        action: str,
        metadata: dict[str, object] | None = None,
    ) -> None:
        previous = self._state(alert)
        alert.status = status
        self.audit(
            alert,
            action=action,
            actor_user_id=actor_id,
            previous=previous,
            new=self._state(alert),
            metadata=metadata,
        )

    def audit(
        self,
        alert: Alert,
        *,
        action: str,
        actor_user_id: uuid.UUID | None,
        previous: dict[str, object] | None,
        new: dict[str, object] | None,
        metadata: dict[str, object] | None = None,
    ) -> None:
        self.session.add(
            AuditEvent(
                actor_user_id=actor_user_id,
                provider_id=alert.provider_id,
                action=action,
                entity_type="alert",
                entity_id=alert.id,
                correlation_id=str(alert.id),
                metadata_json={
                    "advisory_only": True,
                    "human_review_required": True,
                    **(metadata or {}),
                },
                previous_state_summary=previous,
                new_state_summary=new,
                created_at=datetime.now(UTC),
            )
        )

    def to_result(self, alert: Alert) -> AlertResult:
        evidence = tuple(
            AlertEvidence(row.evidence_type, row.payload)
            for row in self.session.scalars(
                select(EvidenceItem)
                .where(EvidenceItem.alert_id == alert.id)
                .order_by(EvidenceItem.created_at, EvidenceItem.id)
            )
        )
        confidence = self.session.scalar(
            select(ConfidenceAssessment.confidence)
            .where(
                ConfidenceAssessment.subject_type == "alert",
                ConfidenceAssessment.subject_id == alert.id,
            )
            .order_by(ConfidenceAssessment.created_at.desc())
        )
        audits = tuple(
            AlertAudit(
                action=row.action,
                actor_user_id=row.actor_user_id,
                previous_state=row.previous_state_summary,
                new_state=row.new_state_summary,
                created_at=row.created_at,
            )
            for row in self.session.scalars(
                select(AuditEvent)
                .where(AuditEvent.entity_type == "alert", AuditEvent.entity_id == alert.id)
                .order_by(AuditEvent.created_at, AuditEvent.id)
            )
        )
        return AlertResult(
            alert_id=alert.id,
            alert_type=alert.alert_type,
            severity=alert.priority,
            provider_id=alert.provider_id,
            agent_id=alert.agent_id,
            evidence=evidence,
            confidence=Decimal("0") if confidence is None else Decimal(confidence),
            recommended_next_step=alert.recommended_next_step or "Human review required.",
            owner_user_id=alert.owner_user_id,
            status=alert.status,
            summary=alert.summary,
            human_review_required=alert.human_review_required,
            created_at=alert.created_at,
            audit_trail=audits,
        )

    def _scope_query(self, scope: AccessScope) -> Select[tuple[Alert]]:
        query = select(Alert).join(Agent, Agent.id == Alert.agent_id)
        if scope.global_access:
            return query
        conditions = []
        if scope.provider_ids:
            conditions.append(Alert.provider_id.in_(scope.provider_ids))
        if scope.area_ids:
            conditions.append(Agent.area_id.in_(scope.area_ids))
        return query.where(or_(*conditions) if conditions else false())

    @staticmethod
    def _state(alert: Alert) -> dict[str, object]:
        return {
            "status": alert.status.value,
            "owner_user_id": None if alert.owner_user_id is None else str(alert.owner_user_id),
        }
