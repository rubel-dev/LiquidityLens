from fastapi.testclient import TestClient

from app.main import create_app


def test_readiness_success(monkeypatch):
    monkeypatch.setattr("app.api.routes.readiness.check_database_ready", lambda settings: True)
    client = TestClient(create_app())

    response = client.get("/api/v1/readiness")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_readiness_failure(monkeypatch):
    monkeypatch.setattr("app.api.routes.readiness.check_database_ready", lambda settings: False)
    client = TestClient(create_app())

    response = client.get("/api/v1/readiness", headers={"X-Request-ID": "req-test"})

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "service_unavailable",
            "message": "Database is unavailable.",
            "correlation_id": "req-test",
        }
    }


def test_readiness_error_response_does_not_expose_secrets(monkeypatch):
    secret_url = "postgresql+psycopg://postgres:super-secret@localhost:5432/private"
    monkeypatch.setenv("DATABASE_SYNC_URL", secret_url)
    monkeypatch.setattr("app.api.routes.readiness.check_database_ready", lambda settings: False)
    client = TestClient(create_app())

    response = client.get("/api/v1/readiness")
    body = response.text

    assert response.status_code == 503
    assert "super-secret" not in body
    assert secret_url not in body
