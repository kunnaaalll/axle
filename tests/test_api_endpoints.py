import pytest
from web.api.app import create_app
from web.api.auth import ADMIN_PASSWORD_HASH

@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"

def test_login_failure(client):
    response = client.post("/auth/login", json={"password": "wrongpassword"})
    assert response.status_code == 401
    assert not response.json["success"]

def test_unauthorized_access(client):
    response = client.get("/monitor/metrics")
    assert response.status_code == 401
    assert not response.json["success"]

def test_projects_endpoint(client):
    # Test requires auth
    response = client.get("/projects/")
    assert response.status_code == 401
