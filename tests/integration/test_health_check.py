"""
Integration test for health check endpoint.
Validates that the /health endpoint returns correct response.
"""
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def test_health_check_endpoint():
    """Test that health check endpoint returns expected response"""
    response = client.get("/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Smart Canteen Manager API"
    assert data["version"] == "1.0.0"


def test_root_endpoint():
    """Test that root endpoint returns welcome message"""
    response = client.get("/")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "Smart Canteen Manager API" in data["message"]
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"
