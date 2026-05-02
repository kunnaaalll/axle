"""
API Integration Tests (T-129)

Tests the Flask API endpoints for health, auth, and protected routes.
"""
import pytest
from web.api.app import create_app
from web.api.auth import ACTIVE_SESSIONS


@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_token(client):
    """Get a valid auth token by logging in."""
    # We need to use werkzeug to generate a valid hash for 'testpass'
    import os
    from werkzeug.security import generate_password_hash
    # Temporarily set the password hash
    import web.api.auth as auth_module
    original_hash = auth_module.ADMIN_PASSWORD_HASH
    auth_module.ADMIN_PASSWORD_HASH = generate_password_hash("testpass", method="pbkdf2:sha256")

    response = client.post("/auth/login", json={"password": "testpass"})
    assert response.status_code == 200
    token = response.json["token"]

    yield token

    # Cleanup
    auth_module.ADMIN_PASSWORD_HASH = original_hash
    ACTIVE_SESSIONS.discard(token)


# ─── Health ───
class TestHealth:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json["status"] == "ok"
        assert response.json["version"] == "1.0.0"


# ─── Auth ───
class TestAuth:
    def test_login_missing_password(self, client):
        response = client.post("/auth/login", json={})
        assert response.status_code == 400

    def test_login_wrong_password(self, client):
        response = client.post("/auth/login", json={"password": "wrong"})
        assert response.status_code == 401
        assert not response.json["success"]

    def test_login_success(self, client, auth_token):
        assert auth_token is not None
        assert len(auth_token) == 64  # token_hex(32)

    def test_logout(self, client, auth_token):
        response = client.post("/auth/logout", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        assert response.json["success"]


# ─── Protected Routes ───
class TestProtectedRoutes:
    def test_metrics_requires_auth(self, client):
        response = client.get("/monitor/metrics")
        assert response.status_code == 401

    def test_projects_requires_auth(self, client):
        response = client.get("/projects/")
        assert response.status_code == 401

    def test_secrets_requires_auth(self, client):
        response = client.get("/secrets/")
        assert response.status_code == 401

    def test_deploy_requires_auth(self, client):
        response = client.post("/deploy/", json={"url": "https://github.com/test/repo"})
        assert response.status_code == 401

    def test_deploy_status_requires_auth(self, client):
        response = client.get("/deploy/status")
        assert response.status_code == 401

    def test_chat_requires_auth(self, client):
        response = client.post("/chat/", json={"query": "hello"})
        assert response.status_code == 401

    def test_invalid_token_rejected(self, client):
        response = client.get("/monitor/metrics", headers={
            "Authorization": "Bearer invalid_token_12345"
        })
        assert response.status_code == 401


# ─── Deploy Validation ───
class TestDeployValidation:
    def test_deploy_missing_url(self, client, auth_token):
        response = client.post("/deploy/", json={}, headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 400
        assert "URL is required" in response.json["error"]

    def test_deploy_status_when_idle(self, client, auth_token):
        response = client.get("/deploy/status", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        assert response.json["success"]


# ─── Secrets Validation ───
class TestSecretsValidation:
    def test_add_secret_missing_fields(self, client, auth_token):
        response = client.post("/secrets/", json={"key": "TEST"}, headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 400

    def test_projects_not_found(self, client, auth_token):
        response = client.get("/projects/nonexistent", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 404
