"""Gemeinsame Pytest-Fixtures.

Integration-Tests (``@pytest.mark.integration``) brauchen eine Postgres-Test-DB.
Ohne ``TEST_DATABASE_URL`` werden sie automatisch übersprungen. Unit-Tests
(Evaluator, Strategien) laufen immer.
"""

from __future__ import annotations

import os

_test_db_url = os.environ.get("TEST_DATABASE_URL")
if _test_db_url:
    os.environ["DATABASE_URL"] = _test_db_url
os.environ.setdefault("SESSION_SECRET", "test-session-secret")
os.environ.setdefault("APP_ENV", "test")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, SessionLocal, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402
from app.security import hash_password  # noqa: E402

INTEGRATION_MARKER = "integration"


def pytest_collection_modifyitems(config, items):
    if _test_db_url:
        return
    skip_marker = pytest.mark.skip(reason="TEST_DATABASE_URL nicht gesetzt")
    for item in items:
        if INTEGRATION_MARKER in item.keywords:
            item.add_marker(skip_marker)


@pytest.fixture(scope="session")
def _db_schema():
    if not _test_db_url:
        pytest.skip("TEST_DATABASE_URL nicht gesetzt")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(_db_schema):
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        with engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                conn.execute(table.delete())


@pytest.fixture
def client(db_session):
    def _get_db_override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_db_override
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def user_factory(db_session):
    def _make(username: str = "admin", password: str = "password123", role: str = "admin") -> User:
        user = User(username=username, password_hash=hash_password(password), role=role)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _make


@pytest.fixture
def admin_user(user_factory):
    return user_factory(username="admin", password="password123")


@pytest.fixture
def authed_client(client, admin_user):
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "password123"})
    assert response.status_code == 200, response.text
    return client
