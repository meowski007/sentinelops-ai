def test_health_check_returns_healthy(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "SentinelOps AI"
    assert data["database"] == "healthy"
    assert "uptime_seconds" in data
    assert "timestamp" in data
