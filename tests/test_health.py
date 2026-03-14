"""Tests for the health check endpoint."""


def test_health_returns_200(client):
    """GET /health returns 200 with correct payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "medbridge-health-coach"
    assert data["version"] == "1.0.0"


def test_health_response_keys(client):
    """Health response contains exactly the expected keys."""
    response = client.get("/health")
    data = response.json()
    assert set(data.keys()) == {"status", "service", "version"}
