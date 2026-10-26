def test_list_incidents(client):
    response = client.get("/api/incidents")
    assert response.status_code == 200
    incidents = response.json()
    assert len(incidents) >= 4
    first = incidents[0]
    assert "id" in first
    assert "severity" in first
    assert "status" in first

def test_filter_incidents_by_severity(client):
    response = client.get("/api/incidents?severity=CRITICAL")
    assert response.status_code == 200
    incidents = response.json()
    assert len(incidents) > 0
    for inc in incidents:
        assert inc["severity"] == "CRITICAL"

def test_filter_incidents_by_status(client):
    response = client.get("/api/incidents?status=TRIGGERED")
    assert response.status_code == 200
    incidents = response.json()
    for inc in incidents:
        assert inc["status"] == "TRIGGERED"

def test_get_incident_by_id_success(client):
    response = client.get("/api/incidents/INC-2026-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "INC-2026-001"
    assert data["affected_service_id"] == "api-gateway"

def test_get_incident_by_id_not_found(client):
    response = client.get("/api/incidents/NON_EXISTENT_ID")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_update_incident_status(client):
    response = client.patch("/api/incidents/INC-2026-001", json={"status": "ACKNOWLEDGED"})
    assert response.status_code == 200
    assert response.json()["status"] == "ACKNOWLEDGED"

def test_get_incident_timeline(client):
    response = client.get("/api/incidents/INC-2026-001/timeline")
    assert response.status_code == 200
    timeline = response.json()
    assert len(timeline) > 0
    # Check that events have required schema fields
    for item in timeline:
        assert "timestamp" in item
        assert "type" in item
        assert "title" in item
