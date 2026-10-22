## Refactor around responsibilities

Keep your existing tests passing while moving code. Start with this layout:

```text
taskboard-learning/
  app/
    __init__.py
    main.py       # app construction and router registration
    tasks.py      # task HTTP boundary
    schemas.py    # input/output contracts
    config.py     # environment settings
  tests/
```

In `tasks.py`, replace `app = FastAPI()` with a router and change decorators from `@app` to `@router`. Keep the in-memory dictionary here temporarily:

```python
from fastapi import APIRouter
router = APIRouter(prefix="/tasks", tags=["tasks"])

# Route paths become "" and "/{task_id}" because the prefix supplies /tasks.
# Move the existing handlers below this declaration.
```

`main.py` now constructs the app and connects the router:

```python
from fastapi import FastAPI
from .tasks import router as tasks_router

app = FastAPI(title="Taskboard API", version="1.0.0")
app.include_router(tasks_router)

@app.get("/health/live")
def live():
    return {"status": "ok"}
```

A router groups related HTTP behavior. A schema defines a wire contract. A service can coordinate a business workflow that spans several models; a repository can encapsulate repeated queries when that abstraction earns its place. Do not add a service/repository interface for every trivial one-line operation. In our final reference, routers stay small and `owned_task` centralizes the authorization-sensitive lookup.

Dependencies should point inward: the app imports routers; routers import schemas and data access. Models should not import the FastAPI app. If imports form a circle, move a shared concept into a lower-level module rather than hiding the cycle inside random functions.

## Lab: refactor with evidence

Move one route at a time, run the existing tests after each move, and compare `/openapi.json` before and after. Preserve the public paths and response shapes. Add a tag and summary for the create operation and verify Swagger groups it correctly.

Your module 2 test fixture currently resets `main.tasks`. After moving storage to `app/tasks.py`, import it with `from app import tasks as task_routes`, reset `task_routes.tasks` and `task_routes.next_id`, and keep `TestClient(main.app)`. This is fixture maintenance caused by temporary dictionary storage; the HTTP assertions stay unchanged.

**Checkpoint:** `python -m uvicorn app.main:app --reload` still works from the learning project root, and none of the contract tests needed changing.

Reference: [Bigger applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/).

<!-- lesson -->
## Dependencies are explicit resource providers

FastAPI resolves dependencies when handling a request. This example is a complete, disposable dependency experiment; save it as `dependency_demo.py` and run `python -m uvicorn dependency_demo:app --reload`:

```python
from typing import Annotated
from fastapi import Depends, FastAPI

app = FastAPI()

def get_prefix():
    return "Taskboard"

@app.get("/label")
def label(prefix: Annotated[str, Depends(get_prefix)]):
    return {"label": prefix}
```

To override it in a test, use the exact same function object:

```python
from fastapi.testclient import TestClient
from dependency_demo import app, get_prefix

app.dependency_overrides[get_prefix] = lambda: "Test label"
try:
    with TestClient(app) as client:
        assert client.get("/label").json() == {"label": "Test label"}
finally:
    app.dependency_overrides.clear()
```

A dependency with `yield` acquires a resource, provides it and cleans it up when its scope ends. Module 4 uses that pattern for one database session per request. Dependencies are not magic when you call an ordinary Python function: pass resolved resources as normal arguments to internal helpers.

## Configuration belongs outside route logic

Install `pydantic-settings` and create `config.py`:

```python
from functools import lru_cache
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./taskboard.sqlite"
    jwt_secret: SecretStr = Field(min_length=32)
    cors_origins: list[str] = []

@lru_cache
def get_settings():
    return Settings()
```

Generate a secret with `python -c "import secrets; print(secrets.token_hex(32))"`, save it as `JWT_SECRET=...` in a local `.env`, and ignore `.env` in Git. The reference's `.env.example` documents names; its placeholder must be replaced. SecretStr masks representation; it does not encrypt storage or excuse logging the unwrapped value.

## Lab: fail early

Instantiate settings with no secret, a five-character secret and a valid secret. Assert validation rejects the first two. Override `DATABASE_URL` using the environment and check that it takes precedence over the `.env` value. Clear `get_settings.cache_clear()` when a settings-focused test intentionally changes environment values; ordinary request tests should set configuration before importing the app.

Reference: [Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) and [settings](https://fastapi.tiangolo.com/advanced/settings/).
