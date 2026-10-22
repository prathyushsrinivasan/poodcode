## Design behavior before implementation

Write the API contract in a README. A resource is a task; the method describes the operation.

| Method | Path | Success | Important failures |
|---|---|---|---|
| POST | /tasks | 201 + public task | 422 invalid body |
| GET | /tasks | 200 + list | 422 invalid pagination |
| GET | /tasks/{id} | 200 + public task | 404 missing, 422 invalid ID |
| PATCH | /tasks/{id} | 200 + updated task | 404 missing, 422 invalid changes |
| DELETE | /tasks/{id} | 204, empty | 404 missing |

Authentication will add 401 and ownership checks later. Keep the contract independent of the storage mechanism.

Start with these models in `app/schemas.py`:

```python
from typing import Annotated
from pydantic import BaseModel, ConfigDict, StringConstraints

Title = Annotated[str, StringConstraints(
    strip_whitespace=True, min_length=1, max_length=120
)]

class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: Title

class TaskRead(BaseModel):
    id: int
    title: str
    done: bool
```

Whitespace stripping happens before the length constraint. `extra="forbid"` rejects fields the client is not allowed to submit. Use separate request, response and storage models: each has a different responsibility. In the database version, `TaskRead` also gets `ConfigDict(from_attributes=True)` so it can read ORM attributes.

`TaskCreate` inherits validation behavior from BaseModel. `Title` is an alias for a constrained string, not a new database column. Start by instantiating `TaskCreate(title="Learn")` in a Python console before wiring it to HTTP. A valid HTTP body is `{"title":"Learn"}`; unlike Python source it uses JSON syntax.

## Implement a vertical slice

Replace the health-only main file with the following plus your health route:

```python
from fastapi import FastAPI, HTTPException
from .schemas import TaskCreate, TaskRead

app = FastAPI()
tasks: dict[int, dict] = {}
next_id = 1

@app.post("/tasks", response_model=TaskRead, status_code=201)
def create_task(body: TaskCreate):
    global next_id
    task = {"id": next_id, "title": body.title, "done": False}
    tasks[next_id] = task
    next_id += 1
    return task

@app.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(404, "Task not found")
    return tasks[task_id]
```

This dictionary and counter are only a single-process teaching stage. They reset on restart and are not a concurrent persistence design. Do not deploy this storage.

## Lab: test the boundary

Use `/docs` to create a task. Try `{"title":" "}`, an absent title and an extra `owner_id`. Expect 422 for each. Try an absent numeric ID and expect 404. Temporarily add `internal_note` to the stored dictionary and prove it is filtered out by `response_model=TaskRead`.

## Route order and parameter sources

FastAPI checks routes in registration order. If you later add a static path such as `/tasks/stats`, register it before `/tasks/{task_id}`. Otherwise `stats` can be treated as the dynamic ID and produce a validation error. Add a tiny static route, deliberately put it after the dynamic route, then move it before and verify the difference.

A value whose name appears in the path comes from that path. Simple remaining arguments such as `limit: int = 20` normally come from the query string; a Pydantic model argument comes from the body. Explicit `Path`, `Query`, `Header` and `Cookie` declarations add constraints or remove ambiguity. Module 3 builds on these boundaries with dependencies.

Reference: [Request bodies](https://fastapi.tiangolo.com/tutorial/body/) and [response models](https://fastapi.tiangolo.com/tutorial/response-model/).

<!-- lesson -->
## Partial updates distinguish omission from false

Add this model in `schemas.py`:

```python
from pydantic import model_validator

class TaskPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: Title | None = None
    done: bool | None = None

    @model_validator(mode="after")
    def reject_null(self):
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Omit unchanged fields; null is not allowed")
        return self
```

For this API, omitted means unchanged, explicit null is invalid, and an empty object is a valid no-op. Other APIs can choose different semantics, but make the choice explicit. A nullable annotation makes omission convenient here; the validator forbids explicitly supplied nulls before they can hit non-null database columns.

Add routes in `main.py` (and import `TaskPatch`):

```python
from typing import Annotated
from fastapi import Query, Response

@app.get("/tasks", response_model=list[TaskRead])
def list_tasks(limit: Annotated[int, Query(ge=1, le=100)] = 20):
    return list(tasks.values())[:limit]

@app.patch("/tasks/{task_id}", response_model=TaskRead)
def patch_task(task_id: int, body: TaskPatch):
    task = read_task(task_id)
    task.update(body.model_dump(exclude_unset=True))
    return task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    read_task(task_id)
    del tasks[task_id]
    return Response(status_code=204)
```

`exclude_unset=True` includes an explicitly supplied `False`; `if body.done:` would silently ignore it. `HTTPException` interrupts normal handling and becomes an HTTP error response. A successful 204 contains no JSON body.

## Read test failures before adding more features

Save `tests/test_tasks.py`. For this dictionary stage, a fresh fixture resets state between tests:

```python
import pytest
from fastapi.testclient import TestClient
from app import main

@pytest.fixture
def client():
    main.tasks.clear()
    main.next_id = 1
    with TestClient(main.app) as test_client:
        yield test_client

def test_task_round_trip(client):
    created = client.post("/tasks", json={"title": "Ship"})
    assert created.status_code == 201
    path = f'/tasks/{created.json()["id"]}'
    assert client.patch(path, json={"done": True}).json()["done"] is True
    changed = client.patch(path, json={"done": False})
    assert changed.json() == {"id": 1, "title": "Ship", "done": False}
    deleted = client.delete(path)
    assert deleted.status_code == 204 and deleted.content == b""
    assert client.get(path).status_code == 404
```

A fixture is reusable test setup: pytest supplies the `client` argument from the function with the same name. Code before `yield` prepares the test, the yielded client is used by the test, and cleanup resumes afterward. In module 3 the dictionary moves into `app.tasks`, so change the reset target there. Module 4 replaces this fixture with an isolated database; module 8 explores fixture design and failure coverage in depth.

## Lab: a request sequence

Write a TestClient test that creates a task, marks it done, changes done back to false, checks that the title survived, deletes it, and confirms detail now returns 404. Add failure cases for null and blank titles. Reset the teaching dictionary and counter for each test until you replace them with a fixture-scoped database in module 8.

**Checkpoint:** submit `{"done":false}` to a task currently marked true. The response must show false, with its original title. Then delete a middle task and create another: the monotonic counter must not overwrite an existing ID.

**Stretch:** implement offset and done filtering. Try `?done=false` and explain why checking `if done:` would lose that filter. Move to persistent SQL in module 4 before adding multiple workers.

Reference: [Body updates](https://fastapi.tiangolo.com/tutorial/body-updates/) and [handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/).
