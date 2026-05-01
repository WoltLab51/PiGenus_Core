def test_health_returns_200(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "uptime_seconds" in data
    assert "database" in data


def test_detailed_health_returns_200(client):
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "metrics" in data
