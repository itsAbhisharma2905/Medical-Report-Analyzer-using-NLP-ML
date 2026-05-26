from fastapi.testclient import TestClient

from api.server import app


def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_text():
    client = TestClient(app)
    response = client.post(
        "/analyze",
        json={"text": "Patient has fever and hypertension. BP 140/90. CBC advised.", "persist": False},
    )
    assert response.status_code == 200
    assert "entities" in response.json()
