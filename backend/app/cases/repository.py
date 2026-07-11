import uuid
from datetime import UTC, datetime

from sqlalchemy import Select, false, or_, select
from sqlalchemy.orm import Session

from app.auth.scope import AccessScope
from app.cases.exceptions import CaseConflictError, CaseNotFoundError
from app.cases.schemas import (
    CaseHistoryResult,
    CaseNoteResult,
    CaseResult,
    EscalationResult,
)
from app.persistence.models.agent import Agent
from app.persistence.models.alert import Alert
from app.persistence.models.audit import AuditEvent
from app.persistence.models.case import Case, CaseNote, CaseStatusHistory, Escalation
from app.persistence.models.enums import CaseStatus


class CaseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_cases(
        self,
        scope: AccessScope,
        *,
        provider_id: uuid.UUID | None = None,
        status: CaseStatus | None = None,
    ) -> tuple[CaseResult, ...]:
        query = self._scope_query(scope)
        if provider_id is not None:
            query = query.where(Case.provider_id == provider_id)
        if status is not None:
            query = query.where(Case.status == status)
        rows = self.session.scalars(query.order_by(Case.updated_at.desc(), Case.id)).all()
        return tuple(self.to_result(row) for row in rows)

    def require_case(self, case_id: uuid.UUID, scope: AccessScope) -> Case:
        row = self.session.scalar(self._scope_query(scope).where(Case.id == case_id))
        if row is None:
            raise CaseNotFoundError("case not found in authorized scope")
        return row

    def require_alert(self, alert_id: uuid.UUID, scope: AccessScope) -> Alert:
        query = select(Alert).join(Agent, Agent.id == Alert.agent_id).where(Alert.id == alert_id)
        if not scope.global_access:
            conditions = []
            if scope.provider_ids:
                conditions.append(Alert.provider_id.in_(scope.provider_ids))
            if scope.area_ids:
                conditions.append(Agent.area_id.in_(scope.area_ids))
            query = query.where(or_(*conditions) if conditions else false())
        row = self.session.scalar(query)
        if row is None:
            raise CaseNotFoundError("source alert not found in authorized scope")
        return row

    def create(self, alert: Alert, actor_id: uuid.UUID, title: str | None) -> Case:
        existing = self.session.scalar(select(Case).where(Case.origin_alert_id == alert.id))
        if existing is not None:
            return existing
        initial_status = {
            "acknowledged": CaseStatus.ACKNOWLEDGED,
            "escalated": CaseStatus.ESCALATED,
            "resolved": CaseStatus.RESOLVED,
            "closed": CaseStatus.CLOSED,
        }.get(alert.status.value, CaseStatus.OPEN)
        case = Case(
            id=uuid.uuid4(),
            origin_alert_id=alert.id,
            provider_id=alert.provider_id,
            agent_id=alert.agent_id,
            owner_user_id=alert.owner_user_id,
            status=initial_status,
            title=title or alert.summary[:200],
            version=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.session.add(case)
        self.session.flush([case])
        self.session.add(
            CaseStatusHistory(
                case_id=case.id,
                from_status=None,
                to_status=initial_status,
                actor_user_id=actor_id,
                reason="case created from advisory alert",
                created_at=datetime.now(UTC),
            )
        )
        self.audit(
            case,
            action="case.created",
            actor_id=actor_id,
            previous=None,
            new=self._state(case),
            metadata={"origin_alert_id": str(alert.id)},
        )
        return case

    def add_note(self, case: Case, actor_id: uuid.UUID, body: str) -> None:
        self.session.add(
            CaseNote(
                case_id=case.id,
                author_user_id=actor_id,
                note=body,
                created_at=datetime.now(UTC),
            )
        )
        self.audit(
            case,
            action="case.note_added",
            actor_id=actor_id,
            previous=self._state(case),
            new=self._state(case),
            metadata={"note": body},
        )

    def transition(
        self,
        case: Case,
        *,
        target: CaseStatus,
        actor_id: uuid.UUID,
        reason: str,
        expected_version: int | None,
    ) -> None:
        if expected_version is not None and expected_version != case.version:
            raise CaseConflictError("case version conflict")
        previous_status = case.status
        previous = self._state(case)
        case.status = target
        case.version += 1
        case.updated_at = datetime.now(UTC)
        self.session.add(
            CaseStatusHistory(
                case_id=case.id,
                from_status=previous_status,
                to_status=target,
                actor_user_id=actor_id,
                reason=reason,
                created_at=datetime.now(UTC),
            )
        )
        self.audit(
            case,
            action=f"case.{target.value}",
            actor_id=actor_id,
            previous=previous,
            new=self._state(case),
            metadata={"reason": reason},
        )

    def add_escalation(
        self,
        case: Case,
        *,
        from_role: str,
        to_role: str,
        reason: str,
    ) -> None:
        self.session.add(
            Escalation(
                case_id=case.id,
                from_role=from_role,
                to_role=to_role,
                reason=reason,
                created_at=datetime.now(UTC),
            )
        )

    def audit(
        self,
        case: Case,
        *,
        action: str,
        actor_id: uuid.UUID,
        previous: dict[str, object] | None,
        new: dict[str, object] | None,
        metadata: dict[str, object] | None = None,
    ) -> None:
        self.session.add(
            AuditEvent(
                actor_user_id=actor_id,
                provider_id=case.provider_id,
                action=action,
                entity_type="case",
                entity_id=case.id,
                correlation_id=str(case.id),
                metadata_json=metadata or {},
                previous_state_summary=previous,
                new_state_summary=new,
                created_at=datetime.now(UTC),
            )
        )

    def to_result(self, case: Case) -> CaseResult:
        notes = tuple(
            CaseNoteResult(row.id, row.author_user_id, row.note, row.created_at)
            for row in self.session.scalars(
                select(CaseNote)
                .where(CaseNote.case_id == case.id)
                .order_by(CaseNote.created_at, CaseNote.id)
            )
        )
        history = tuple(
            CaseHistoryResult(
                row.from_status,
                row.to_status,
                row.actor_user_id,
                row.reason,
                row.created_at,
            )
            for row in self.session.scalars(
                select(CaseStatusHistory)
                .where(CaseStatusHistory.case_id == case.id)
                .order_by(CaseStatusHistory.created_at, CaseStatusHistory.id)
            )
        )
        escalations = tuple(
            EscalationResult(row.id, row.from_role, row.to_role, row.reason, row.created_at)
            for row in self.session.scalars(
                select(Escalation)
                .where(Escalation.case_id == case.id)
                .order_by(Escalation.created_at, Escalation.id)
            )
        )
        audits = tuple(
            self.session.scalars(
                select(AuditEvent.id)
                .where(AuditEvent.entity_type == "case", AuditEvent.entity_id == case.id)
                .order_by(AuditEvent.created_at, AuditEvent.id)
            )
        )
        resolution = next(
            (
                item.body.removeprefix("Resolution: ")
                for item in reversed(notes)
                if item.body.startswith("Resolution: ")
            ),
            None,
        )
        return CaseResult(
            case_id=case.id,
            origin_alert_id=case.origin_alert_id,
            provider_id=case.provider_id,
            agent_id=case.agent_id,
            owner_user_id=case.owner_user_id,
            status=case.status,
            title=case.title,
            version=case.version,
            created_at=case.created_at,
            updated_at=case.updated_at,
            notes=notes,
            status_history=history,
            escalation_history=escalations,
            resolution_information=resolution,
            audit_event_ids=audits,
        )

    def _scope_query(self, scope: AccessScope) -> Select[tuple[Case]]:
        query = select(Case).join(Agent, Agent.id == Case.agent_id)
        if scope.global_access:
            return query
        conditions = []
        if scope.provider_ids:
            conditions.append(Case.provider_id.in_(scope.provider_ids))
        if scope.area_ids:
            conditions.append(Agent.area_id.in_(scope.area_ids))
        return query.where(or_(*conditions) if conditions else false())

    @staticmethod
    def _state(case: Case) -> dict[str, object]:
        return {
            "status": case.status.value,
            "owner_user_id": None if case.owner_user_id is None else str(case.owner_user_id),
            "version": case.version,
        }
