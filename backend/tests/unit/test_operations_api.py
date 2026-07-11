import uuid
from datetime import UTC, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from app.alerts.schemas import AlertAudit, AlertEvidence, AlertResult
from app.api.routes import alerts as alert_routes
from app.api.routes import cases as case_routes
from app.auth.scope import AccessScope, get_access_scope
from app.cases.schemas import CaseResult
from app.main import create_app
from app.persistence.database import get_db_session
from app.persistence.models.enums import AlertPriority, AlertStatus, CaseStatus

NOW = datetime(2026, 7, 11, 12, 0, tzinfo=UTC)
USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000101")
ALERT_ID = uuid.UUID("00000000-0000-0000-0000-000000000201")
CASE_ID = uuid.UUID("00000000-0000-0000-0000-000000000301")
AGENT_ID = uuid.UUID("00000000-0000-0000-0000-000000000401")
PROVIDER_ID = uuid.UUID("00000000-0000-0000-0000-000000000501")


def alert_result(status: AlertStatus = AlertStatus.OPEN) -> AlertResult:
    return AlertResult(
        alert_id=ALERT_ID,
        alert_type="liquidity_shortage",
        severity=AlertPriority.HIGH,
        provider_id=PROVIDER_ID,
        agent_id=AGENT_ID,
        evidence=(AlertEvidence("forecast_summary", {"risk_level": "warning"}),),
        confidence=Decimal("0.7500"),
        recommended_next_step="Human review required.",
        owner_user_id=USER_ID,
        status=status,
        summary="Warning liquidity runway risk requires human review.",
        human_review_required=True,
        created_at=NOW,
        audit_trail=(AlertAudit("alert.created", None, None, {"status": "open"}, NOW),),
    )


def case_result(status: CaseStatus = CaseStatus.ACKNOWLEDGED) -> CaseResult:
    return CaseResult(
        case_id=CASE_ID,
        origin_alert_id=ALERT_ID,
        provider_id=PROVIDER_ID,
        agent_id=AGENT_ID,
        owner_user_id=USER_ID,
        status=status,
        title="Synthetic case",
        version=1,
        created_at=NOW,
        updated_at=NOW,
        notes=(),
        status_history=(),
        escalation_history=(),
        resolution_information=None,
        audit_event_ids=(),
    )


class FakeAlertService:
    def __init__(self, _session: object) -> None:
        pass

    def list_alerts(self, _scope: AccessScope, **_filters: object) -> tuple[AlertResult, ...]:
        return (alert_result(),)

    def get_alert(self, _alert_id: uuid.UUID, _scope: AccessScope) -> AlertResult:
        return alert_result()

    def assign(
        self, _alert_id: uuid.UUID, _assignee: uuid.UUID, _scope: AccessScope
    ) -> AlertResult:
        return alert_result()

    def acknowledge(
        self, _alert_id: uuid.UUID, _scope: AccessScope, _note: str | None
    ) -> AlertResult:
        return alert_result(AlertStatus.ACKNOWLEDGED)


class FakeCaseService:
    def __init__(self, _session: object) -> None:
        pass

    def list_cases(self, _scope: AccessScope, **_filters: object) -> tuple[CaseResult, ...]:
        return (case_result(),)

    def get_case(self, _case_id: uuid.UUID, _scope: AccessScope) -> CaseResult:
        return case_result()

    def create_from_alert(
        self, _alert_id: uuid.UUID, _scope: AccessScope, **_values: object
    ) -> CaseResult:
        return case_result()

    def escalate(self, _case_id: uuid.UUID, _scope: AccessScope, **_values: object) -> CaseResult:
        return case_result(CaseStatus.ESCALATED)

    def resolve(self, _case_id: uuid.UUID, _scope: AccessScope, **_values: object) -> CaseResult:
        return case_result(CaseStatus.RESOLVED)


def client(monkeypatch) -> TestClient:
    monkeypatch.setattr(alert_routes, "AlertService", FakeAlertService)
    monkeypatch.setattr(case_routes, "CaseService", FakeCaseService)
    app = create_app()
    app.dependency_overrides[get_access_scope] = lambda: AccessScope(
        USER_ID, frozenset({"ops"}), frozenset({PROVIDER_ID}), frozenset()
    )
    app.dependency_overrides[get_db_session] = lambda: object()
    return TestClient(app)


def test_alert_api_list_detail_assignment_and_acknowledgement(monkeypatch) -> None:
    api = client(monkeypatch)

    assert api.get("/api/v1/alerts").status_code == 200
    assert api.get(f"/api/v1/alerts/{ALERT_ID}").json()["provider_id"] == str(PROVIDER_ID)
    assert (
        api.post(
            f"/api/v1/alerts/{ALERT_ID}/assign",
            json={"assignee_user_id": str(USER_ID)},
        ).status_code
        == 200
    )
    response = api.post(
        f"/api/v1/alerts/{ALERT_ID}/acknowledge",
        json={"note": "Reviewed"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "acknowledged"


def test_case_api_list_detail_create_escalate_and_resolve(monkeypatch) -> None:
    api = client(monkeypatch)

    assert api.get("/api/v1/cases").status_code == 200
    assert api.get(f"/api/v1/cases/{CASE_ID}").status_code == 200
    assert api.post("/api/v1/cases", json={"alert_id": str(ALERT_ID)}).status_code == 201
    escalated = api.post(
        f"/api/v1/cases/{CASE_ID}/escalate",
        json={"to_role": "risk", "reason": "Review required", "expected_version": 1},
    )
    assert escalated.status_code == 200
    assert escalated.json()["status"] == "escalated"
    resolved = api.post(
        f"/api/v1/cases/{CASE_ID}/resolve",
        json={"rationale": "Reviewed", "expected_version": 1},
    )
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "resolved"


def test_operations_api_rejects_invalid_uuid_and_empty_lifecycle_payload(monkeypatch) -> None:
    api = client(monkeypatch)

    assert api.get("/api/v1/alerts/not-a-uuid").status_code == 422
    assert (
        api.post(
            f"/api/v1/cases/{CASE_ID}/escalate",
            json={"to_role": "", "reason": ""},
        ).status_code
        == 422
    )
    assert api.post(f"/api/v1/cases/{CASE_ID}/resolve", json={"rationale": ""}).status_code == 422


def test_openapi_contains_only_requested_operations_endpoints(monkeypatch) -> None:
    api = client(monkeypatch)
    paths = api.get("/openapi.json").json()["paths"]

    expected = {
        "/api/v1/alerts",
        "/api/v1/alerts/{alert_id}",
        "/api/v1/alerts/{alert_id}/acknowledge",
        "/api/v1/alerts/{alert_id}/assign",
        "/api/v1/cases",
        "/api/v1/cases/{case_id}",
        "/api/v1/cases/{case_id}/escalate",
        "/api/v1/cases/{case_id}/resolve",
    }
    assert expected.issubset(paths)
    assert "/api/v1/alerts/{alert_id}/block" not in paths
    assert "/api/v1/alerts/{alert_id}/transfer" not in paths
