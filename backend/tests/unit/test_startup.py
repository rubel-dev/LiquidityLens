from fastapi.testclient import TestClient

from app.main import create_app


def test_application_startup():
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200

