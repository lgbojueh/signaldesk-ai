from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_returns_grounded_result():
    response = client.post(
        "/api/analyze",
        json={
            "title": "Docker API cannot reach Postgres",
            "description": "After Docker deployment the API returns connection refused when connecting to Postgres.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] in {"Deployment", "Database", "Networking"}
    assert data["sources"]
    assert data["steps"]


def test_ticket_history_and_detail():
    created = client.post(
        "/api/analyze",
        json={
            "title": "Internal DNS failure",
            "description": "The service is reachable by IP but its internal hostname no longer resolves after a network change.",
        },
    )
    assert created.status_code == 200
    ticket_id = created.json()["id"]

    history = client.get("/api/tickets")
    assert history.status_code == 200
    assert any(item["id"] == ticket_id for item in history.json())

    detail = client.get(f"/api/tickets/{ticket_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == ticket_id
    assert detail.json()["sources"]
