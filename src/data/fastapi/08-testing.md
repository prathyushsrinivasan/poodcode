## Tests need their own database

Install the reference's `requirements-dev.txt`, or add pytest and HTTPX to your learning environment. Do not run tests against a development database full of your work or a cloud database. Set test configuration before importing app modules that construct the engine.

Use a fresh in-memory SQLite engine for each test. This fixture is complete when placed in `tests/conftest.py` in the reference project:

```python
import os
os.environ["JWT_SECRET"] = "test-only-secret-" + "x" * 40
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.db import Base, get_db
from app.main import app

@pytest.fixture
def client():
    engine = create_engine("sqlite://", poolclass=StaticPool,
                           connect_args={"check_same_thread": False})
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
```

`create_all` is appropriate for an isolated test fixture checking current model behavior. It does not test your migration history, which needs its own fresh-database migration check. StaticPool lets all request threads in this fixture see the same in-memory database; each test still gets a different engine.

The `with TestClient(app)` context also runs application lifespan startup/shutdown hooks. Clearing overrides in `finally` prevents one fixture from altering later tests. The completed reference keeps its fixture in `test_api.py`; use either placement, not two competing fixtures.

## Lab: write a user helper

Create an `account(client, username)` helper that registers the username, logs in with form data and returns `{"Authorization": "Bearer " + token}`. Assert each setup response's status before indexing its JSON, so a setup failure has a useful error.

Reference: [Testing dependencies](https://fastapi.tiangolo.com/advanced/testing-dependencies/) and [SQLite multithreaded memory databases](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#using-a-memory-database-in-multiple-threads).

<!-- lesson -->
## A meaningful test demonstrates observable behavior

Write this test before reading the final reference suite:

```python
def test_bob_cannot_modify_alices_task(client):
    alice = account(client, "alice")
    bob = account(client, "bob")
    created = client.post("/tasks", headers=alice, json={"title": "Private"})
    assert created.status_code == 201
    task_id = created.json()["id"]
    path = f"/tasks/{task_id}"
    assert client.get("/tasks", headers=bob).json() == []
    assert client.get(path, headers=bob).status_code == 404
    assert client.patch(path, headers=bob, json={"done": True}).status_code == 404
    assert client.delete(path, headers=bob).status_code == 404
    remaining = client.get(path, headers=alice)
    assert remaining.status_code == 200
    assert remaining.json()["done"] is False
```

Then add a CRUD sequence, validation cases, public-user field filtering, duplicate-registration recovery, missing/invalid/expired tokens, disabled users, pagination bounds and empty DELETE content. Use parameterization for inputs with the same expected behavior:

```python
import pytest

@pytest.mark.parametrize("title", ["", "   ", "x" * 121])
def test_rejects_invalid_titles(client, title):
    headers = account(client, "alice")
    response = client.post("/tasks", headers=headers, json={"title": title})
    assert response.status_code == 422
```

Avoid asserting internals such as the exact query text or the order helpers were called unless they are the actual requirement. HTTP tests should survive a refactor that preserves the contract.

## Lab: mutation proves the test is useful

Temporarily remove `Task.owner_id == user_id` from `owned_task`. The security test must fail. Restore it. Temporarily replace the PATCH loop with a truthiness check; your false-update test must fail. Restore it. Temporarily disable expiry verification; your expired-token test must fail. Restore it.

If a deliberate bug does not fail a test, strengthen the assertion before adding more code. Finish with a clean full suite:

```text
python -m pytest -q
```

## Test the real storage boundary too

SQLite is fast for the HTTP behavior suite. PostgreSQL has different types, constraints and transaction behavior. On a disposable PostgreSQL database, run `alembic upgrade head`, `alembic check`, then a registration/login/task smoke sequence using the actual app. Once installed in your learning repository, the supplied CI template starts PostgreSQL and checks the migration history; it also runs a real-connection smoke script.

**Checkpoint:** your tests can be rerun from a clean checkout, do not depend on execution order, and catch the three deliberate regressions.
