def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "verifi-backend"
    assert data["database"] == "not_used"
    assert data["repository"] == "in_memory"
    assert "version" in data
