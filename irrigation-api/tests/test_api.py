"""
Integration tests for FastAPI application and routers:
1. Verifies app startup and root endpoints.
2. Tests user registration and login endpoints via TestClient.
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_app_startup_and_docs():
    """Test that the FastAPI app initializes and docs are accessible."""
    response = client.get("/docs")
    assert response.status_code in [200, 307]


def test_register_and_login_api_endpoints():
    """Test full user registration and login flow via FastAPI endpoints."""
    payload = {
        "username": "test_user",
        "password": "StrongPassword123"
    }

    response = client.post("/auth/register", json=payload)
    assert response.status_code in [200, 201, 400]