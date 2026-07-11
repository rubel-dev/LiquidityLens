import uuid

from sqlalchemy.orm import Session

from app.alerts.repository import AlertRepository
from app.auth.scope import AccessScope
from app.cases.exceptions import CaseAuthorizationError, CaseConflictError
from app.cases.repository import CaseRepository
from app.cases.schemas import CaseResult
from app.persistence.models.enums import AlertStatus, CaseStatus


class CaseService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = CaseRepository(session)
        self.alert_repository = AlertRepository(session)

    def list_cases(
        self,
        scope: AccessScope,
        *,
        provider_id: uuid.UUID | None = None,
        status: CaseStatus | None = None,
    ) -> tuple[CaseResult, ...]:
        return self.repository.list_cases(scope, provider_id=provider_id, status=status)

    def get_case(self, case_id: uuid.UUID, scope: AccessScope) -> CaseResult:
        return self.repository.to_result(self.repository.require_case(case_id, scope))

    def create_from_alert(
        self,
        alert_id: uuid.UUID,
        scope: AccessScope,
        *,
        title: str | None = None,
        initial_note: str | None = None,
    ) -> CaseResult:
        self._require_role(scope, "ops", "risk", "manager")
        with self.session.begin():
            alert = self.repository.require_alert(alert_id, scope)
            case = self.repository.create(alert, scope.user_id, title)
            if initial_note:
                self.repository.add_note(case, scope.user_id, initial_note)
            self.session.flush()
            return self.repository.to_result(case)

    def add_note(self, case_id: uuid.UUID, scope: AccessScope, body: str) -> CaseResult:
        if not body.strip():
            raise CaseConflictError("case note must not be empty")
        with self.session.begin():
            case = self.repository.require_case(case_id, scope)
            self._require_owner_or_role(case.owner_user_id, scope, "risk", "ops", "manager")
            self.repository.add_note(case, scope.user_id, body.strip())
            self.session.flush()
            return self.repository.to_result(case)

    def escalate(
        self,
        case_id: uuid.UUID,
        scope: AccessScope,
        *,
        to_role: str,
        reason: str,
        expected_version: int | None = None,
    ) -> CaseResult:
        if not reason.strip() or not to_role.strip():
            raise CaseConflictError("escalation target and reason are required")
        with self.session.begin():
            case = self.repository.require_case(case_id, scope)
            self._require_owner_or_role(case.owner_user_id, scope, "ops", "risk", "manager")
            if case.status not in {
                CaseStatus.OPEN,
                CaseStatus.ASSIGNED,
                CaseStatus.ACKNOWLEDGED,
            }:
                raise CaseConflictError("case cannot be escalated from its current status")
            from_role = sorted(scope.roles)[0]
            self.repository.add_escalation(
                case,
                from_role=from_role,
                to_role=to_role.strip(),
                reason=reason.strip(),
            )
            self.repository.transition(
                case,
                target=CaseStatus.ESCALATED,
                actor_id=scope.user_id,
                reason=reason.strip(),
                expected_version=expected_version,
            )
            self._sync_alert(case.origin_alert_id, AlertStatus.ESCALATED, scope, "alert.escalated")
            self.session.flush()
            return self.repository.to_result(case)

    def resolve(
        self,
        case_id: uuid.UUID,
        scope: AccessScope,
        *,
        rationale: str,
        expected_version: int | None = None,
    ) -> CaseResult:
        if not rationale.strip():
            raise CaseConflictError("resolution rationale is required")
        with self.session.begin():
            case = self.repository.require_case(case_id, scope)
            self._require_owner_or_role(case.owner_user_id, scope, "risk", "manager")
            if case.status not in {CaseStatus.ACKNOWLEDGED, CaseStatus.ESCALATED}:
                raise CaseConflictError("case must be acknowledged or escalated before resolution")
            self.repository.add_note(case, scope.user_id, f"Resolution: {rationale.strip()}")
            self.repository.transition(
                case,
                target=CaseStatus.RESOLVED,
                actor_id=scope.user_id,
                reason=rationale.strip(),
                expected_version=expected_version,
            )
            self._sync_alert(case.origin_alert_id, AlertStatus.RESOLVED, scope, "alert.resolved")
            self.session.flush()
            return self.repository.to_result(case)

    def close(
        self,
        case_id: uuid.UUID,
        scope: AccessScope,
        *,
        reason: str,
        expected_version: int | None = None,
    ) -> CaseResult:
        self._require_role(scope, "ops", "manager")
        with self.session.begin():
            case = self.repository.require_case(case_id, scope)
            if case.status != CaseStatus.RESOLVED:
                raise CaseConflictError("only a resolved case can be closed")
            self.repository.transition(
                case,
                target=CaseStatus.CLOSED,
                actor_id=scope.user_id,
                reason=reason,
                expected_version=expected_version,
            )
            self._sync_alert(case.origin_alert_id, AlertStatus.CLOSED, scope, "alert.closed")
            self.session.flush()
            return self.repository.to_result(case)

    def _sync_alert(
        self,
        alert_id: uuid.UUID | None,
        status: AlertStatus,
        scope: AccessScope,
        action: str,
    ) -> None:
        if alert_id is None:
            return
        alert = self.alert_repository.require_alert(alert_id, scope)
        self.alert_repository.change_status(
            alert,
            status=status,
            actor_id=scope.user_id,
            action=action,
            metadata={"case_workflow": True},
        )

    @staticmethod
    def _require_role(scope: AccessScope, *roles: str) -> None:
        if not scope.has_any_role(*roles):
            raise CaseAuthorizationError(f"one of these roles is required: {', '.join(roles)}")

    @staticmethod
    def _require_owner_or_role(
        owner_user_id: uuid.UUID | None,
        scope: AccessScope,
        *roles: str,
    ) -> None:
        if owner_user_id != scope.user_id and not scope.has_any_role(*roles):
            raise CaseAuthorizationError("case owner or authorized review role required")
