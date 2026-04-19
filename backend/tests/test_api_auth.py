import pytest

pytestmark = pytest.mark.integration


def test_login_sets_session_cookie_and_returns_user(client, admin_user):
    response = client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "admin"
    assert "session" in response.cookies


def test_login_wrong_password_401(client, admin_user):
    response = client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "wrong"}
    )
    assert response.status_code == 401


def test_login_unknown_user_401(client):
    response = client.post(
        "/api/v1/auth/login", json={"username": "ghost", "password": "x"}
    )
    assert response.status_code == 401


def test_me_requires_auth(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user(authed_client):
    response = authed_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


def test_logout_clears_session(authed_client):
    response = authed_client.post("/api/v1/auth/logout")
    assert response.status_code == 204
    me = authed_client.get("/api/v1/auth/me")
    assert me.status_code == 401
