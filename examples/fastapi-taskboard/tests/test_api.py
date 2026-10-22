import os
from datetime import datetime, timedelta, timezone

os.environ["JWT_SECRET"] = "test-only-secret-" + "x" * 40
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["CORS_ORIGINS"] = '["https://client.example"]'

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.config import get_settings
from app.db import Base, get_db
from app.main import app
from app.models import User
from app.security import password_hash


@pytest.fixture
def client():
    # StaticPool shares the same in-memory SQLite database across request threads.
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    def override_db():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def account(client, username="alice"):
    password = "correct-horse-battery"
    assert client.post("/auth/register", json={"username": username, "password": password}).status_code == 201
    response = client.post("/auth/token", data={"username": username, "password": password})
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    return {"Authorization": "Bearer " + response.json()["access_token"]}


def test_health_and_openapi(client):
    assert client.get("/health/live").json() == {"status": "ok"}
    assert client.get("/health/ready").status_code == 200
    assert "OAuth2PasswordBearer" in client.get("/openapi.json").json()["components"]["securitySchemes"]
    assert client.get("/health/live").headers["x-request-id"]


def test_registration_hashes_and_hides_password(client):
    headers = account(client)
    me = client.get("/auth/me", headers=headers)
    assert set(me.json()) == {"id", "username"}
    for session in app.dependency_overrides[get_db]():
        user = session.scalar(select(User))
        assert user.password_hash != "correct-horse-battery"
        assert password_hash.verify("correct-horse-battery", user.password_hash)


def test_duplicate_username_and_rollback(client):
    account(client)
    assert client.post("/auth/register", json={"username": "ALICE", "password": "another-long-password"}).status_code == 409
    assert client.post("/auth/register", json={"username": "carol", "password": "another-long-password"}).status_code == 201


def test_crud(client):
    headers = account(client)
    result = client.post("/tasks", headers=headers, json={"title": "  Ship API  "})
    assert result.status_code == 201
    task = result.json()
    assert task["title"] == "Ship API" and task["done"] is False
    path = f'/tasks/{task["id"]}'
    assert client.get(path, headers=headers).json() == task
    patched = client.patch(path, headers=headers, json={"done": True})
    assert patched.json()["title"] == "Ship API" and patched.json()["done"] is True
    assert client.delete(path, headers=headers).content == b""
    assert client.get(path, headers=headers).status_code == 404


def test_owner_isolation_on_every_operation(client):
    alice, bob = account(client), account(client, "bob")
    task = client.post("/tasks", headers=alice, json={"title": "Alice private"}).json()
    path = f'/tasks/{task["id"]}'
    assert client.get("/tasks", headers=bob).json() == []
    assert client.get(path, headers=bob).status_code == 404
    assert client.patch(path, headers=bob, json={"done": True}).status_code == 404
    assert client.delete(path, headers=bob).status_code == 404
    assert client.get(path, headers=alice).status_code == 200


@pytest.mark.parametrize("body", [{"title": ""}, {"title": "   "}, {"title": "x" * 121}, {"title": "ok", "owner_id": 7}])
def test_create_validation(client, body):
    assert client.post("/tasks", headers=account(client), json=body).status_code == 422


@pytest.mark.parametrize("body", [{"title": None}, {"done": None}, {"title": " "}, {"owner_id": 7}])
def test_patch_validation(client, body):
    headers = account(client)
    task = client.post("/tasks", headers=headers, json={"title": "Keep me"}).json()
    assert client.patch(f'/tasks/{task["id"]}', headers=headers, json=body).status_code == 422


def test_pagination_filter_and_false_patch(client):
    headers = account(client)
    for title in ["A", "B", "C"]:
        client.post("/tasks", headers=headers, json={"title": title})
    assert [t["title"] for t in client.get("/tasks?limit=1&offset=1", headers=headers).json()] == ["B"]
    client.patch("/tasks/1", headers=headers, json={"done": True})
    assert len(client.get("/tasks?done=false", headers=headers).json()) == 2
    assert client.patch("/tasks/1", headers=headers, json={"done": False}).json()["done"] is False
    for query in ["limit=0", "limit=101", "offset=-1"]:
        assert client.get("/tasks?" + query, headers=headers).status_code == 422


def test_missing_and_invalid_credentials(client):
    assert client.get("/tasks").status_code == 401
    response = client.get("/tasks", headers={"Authorization": "Bearer broken"})
    assert response.status_code == 401 and response.headers["www-authenticate"] == "Bearer"
    for username in ["alice", "unknown"]:
        assert client.post("/auth/token", data={"username": username, "password": "wrong-password"}).status_code == 401


@pytest.mark.parametrize("change", ["expired", "bad-signature", "wrong-audience", "missing-exp", "bad-sub"])
def test_rejects_bad_tokens(client, change):
    account(client)
    now = datetime.now(timezone.utc)
    payload = {"sub": "1", "iat": now, "exp": now + timedelta(minutes=5), "iss": "taskboard", "aud": "taskboard-api"}
    secret = get_settings().jwt_secret.get_secret_value()
    if change == "expired":
        payload["exp"] = now - timedelta(minutes=1)
    elif change == "bad-signature":
        secret = "another-test-secret-" + "y" * 40
    elif change == "wrong-audience":
        payload["aud"] = "another-api"
    elif change == "missing-exp":
        del payload["exp"]
    else:
        payload["sub"] = "not-an-id"
    token = jwt.encode(payload, secret, algorithm="HS256")
    assert client.get("/tasks", headers={"Authorization": "Bearer " + token}).status_code == 401


def test_disabled_user_loses_access(client):
    headers = account(client)
    for session in app.dependency_overrides[get_db]():
        user = session.scalar(select(User))
        user.active = False
        session.commit()
    assert client.get("/tasks", headers=headers).status_code == 401


def test_cors_preflight(client):
    response = client.options("/tasks", headers={"Origin": "https://client.example", "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "authorization,content-type"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://client.example"
    denied = client.options("/tasks", headers={"Origin": "https://untrusted.example", "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in denied.headers


def test_readiness_failure(client):
    class BrokenDb:
        def execute(self, statement):
            raise OperationalError("SELECT 1", {}, Exception("offline"))
    app.dependency_overrides[get_db] = lambda: BrokenDb()
    assert client.get("/health/ready").status_code == 503
    assert client.get("/health/live").status_code == 200
