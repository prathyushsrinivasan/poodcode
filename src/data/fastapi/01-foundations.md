## Start here

No FastAPI, HTTP, database, or cloud experience is assumed. You need a terminal, Python 3.12 or newer, and basic programming skills. The readiness lab below makes those skills explicit. If you have never programmed, first work through a beginner Python course, then return here; a short bridge cannot replace learning a first language. The [official Python tutorial](https://docs.python.org/3/tutorial/) is useful for programmers learning Python, but also assumes basic programming knowledge.

The core course targets beginner to intermediate FastAPI development. Its final project proves you can build, test and deploy this kind of API. Advanced specialization still needs deeper async database work, jobs, caching and real-time systems; see the course audit in `FASTAPI_COURSE_AUDIT.md` for the expansion plan. The course is roughly 80% coding and debugging: read a small example, type it, change it, test it, then build the milestone without looking.

You will build **Taskboard**: users register and log in, then create private tasks. The same project grows through validation, a database, authorization, tests and deployment. Budget 40–50 focused hours for the core, with more time for unfamiliar Python or Docker. Work at your own pace; module numbers are prerequisites, not calendar weeks.

Create a separate learning folder so your Python experiments do not alter the desktop app. Commands below run from that folder unless a lesson says otherwise.

```powershell
mkdir taskboard-learning
cd taskboard-learning
python -m venv .venv
# Windows PowerShell (activation is optional):
.venv\Scripts\Activate.ps1
python -m pip install "fastapi>=0.115,<1" "uvicorn[standard]" httpx pytest
mkdir app
New-Item app/__init__.py
mkdir tests
```

On macOS/Linux use `source .venv/bin/activate` and `touch app/__init__.py`. If activation is unavailable, call `.venv\Scripts\python.exe` directly on Windows or `.venv/bin/python` on Unix. Use `python -m pip`, `python -m pytest` and `python -m uvicorn` to keep commands attached to the selected Python environment.

The complete reference is in `examples/fastapi-taskboard`. Its README includes exact setup, dependency pins, PostgreSQL, migrations, tests, and deployment commands. Build your version before reading the reference.

## Python readiness before framework syntax

Save this as `python_bridge.py` and run `python python_bridge.py`:

```python
def unfinished_titles(tasks: list[dict]) -> list[str]:
    result = []
    for task in tasks:
        if not task["done"]:
            result.append(task["title"])
    return result

tasks = [
    {"title": "Read a request", "done": False},
    {"title": "Install Python", "done": True},
]
assert unfinished_titles(tasks) == ["Read a request"]

try:
    task_id = int("not-a-number")
except ValueError:
    print("An ID must be an integer")
```

A dictionary maps keys to values; a list keeps several values in order. `def` defines a function, indentation groups its body, `return` sends a result to its caller, and `assert` checks an expectation. `try/except` handles a specific failure. You must be able to add a third task, change its done flag and explain the result without copying a solution.

You will also see classes and decorators:

```python
class TaskDraft:
    def __init__(self, title: str):
        self.title = title

def announce(function):
    print(f"Registered {function.__name__}")
    return function

@announce
def say_hello():
    return "hello"

draft = TaskDraft("Learn classes")
assert draft.title == "Learn classes"
assert say_hello() == "hello"
```

A class groups data and behavior. `self` is the instance being used. A decorator receives a function when its definition runs; FastAPI uses a decorator to register a function as a route. You do not need to implement your own decorator to use `@app.get`, but you should recognize what the syntax does.

In later modules, `with resource:` bounds acquisition and cleanup. A generator pauses at `yield`, hands a value to its caller, then resumes; FastAPI uses that pattern to provide a resource and clean it up afterward. Modules 3 and 4 demonstrate the lifecycle before asking you to design it.

## A small Python bridge

```python
from typing import Annotated
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=120)]

def greeting(name: str = "world") -> dict[str, str]:
    return {"message": f"Hello, {name}"}

print(greeting("Ada"))
print(TaskCreate(title="Learn FastAPI").model_dump())
```

Type hints describe values. `str | None` allows a string or `None`; `list[str]` describes a list of strings. `Annotated[T, metadata]` adds constraints while preserving the underlying type. Ordinary Python does not enforce hints by itself. Pydantic uses them to construct and validate data at runtime. FastAPI uses them to describe and validate HTTP inputs.

`from .schemas import TaskCreate` means import from the same package; the dot matters. Run `app.main:app` from the directory containing `app`, rather than running a package file directly.

## Lab: make the types useful

Add `done: bool = False`, create a model with only a title and print it. Then pass a missing title and catch `pydantic.ValidationError`. Try a number as the title and inspect the error. Do not memorize all coercion rules: verify the specific contract your API promises.

**Checkpoint:** you can run a Python file inside the virtual environment and explain a model, a type annotation, an import, and a default argument.

Reference: [Python types in FastAPI](https://fastapi.tiangolo.com/python-types/).

<!-- lesson -->
## Your first app

Put this complete program in `app/main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="Taskboard API")

@app.get("/health/live")
def live():
    return {"status": "ok"}

@app.get("/hello")
def hello(name: str = "world"):
    return {"message": f"Hello, {name}"}
```

```text
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`, expand an endpoint and choose Try it out. Also inspect `/openapi.json`: your code has produced a machine-readable contract. The decorator connects an HTTP method and path to a Python function. Uvicorn is the ASGI server that receives network requests and calls the application.

## Read an HTTP exchange

A client sends a request; your server sends a response. For `GET /hello?name=Ada`, GET is the method, `/hello` is the path, and `name=Ada` is a query parameter. A route such as `/tasks/{task_id}` instead takes an ID from the path. Request headers describe the request or carry credentials. A request body carries data for operations such as creating a task.

The response contains a status code, headers and sometimes a body. JSON is a text data format: objects use braces, strings use double quotes, and booleans are lowercase `true`/`false`. Python dictionaries and `True`/`False` are Python values; FastAPI serializes them into JSON for the client. `Content-Type: application/json` describes that representation.

Typical meanings: 200 success, 201 created, 204 success without a body, 401 missing/invalid credentials, 403 insufficient permission, 404 not found, 405 wrong method, 409 conflict, 422 invalid input and 500 unexpected server failure. You will implement these boundaries rather than memorize the list.

Use `curl.exe` on Windows so PowerShell does not substitute an alias:

```text
curl.exe -i "http://127.0.0.1:8000/hello?name=Ada"
```

Expect HTTP 200, a JSON content type and `{"message":"Hello, Ada"}`. A method is part of the route: POST to this GET-only path should return 405. An unknown path returns 404.

## Test before the app becomes complicated

Create `tests/test_first.py`:

```python
from fastapi.testclient import TestClient
from app.main import app

def test_greeting():
    with TestClient(app) as client:
        response = client.get("/hello", params={"name": "Ada"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Ada"}
```

Run `python -m pytest -q`. No separate Uvicorn process is required for TestClient. Change the greeting to something wrong, observe the failure, then restore it.

## Lab: change the contract

Add `/square/{number}` with `number: int` and return its square. Test `7`, `-3`, and `abc`. The first two reach the function; `abc` should fail validation with 422. Add a health test and prove that POST `/hello` gives 405. Keep assertions focused on status and meaningful fields rather than the exact formatting of validation messages.

**Ready for module 2:** point out the method, path, query, status and JSON body in an actual request. Write a function, dictionary, loop and assertion yourself. If either task is unfamiliar, repeat the bridge lab before introducing validation models.

**Debugging:** “Could not import module” usually means the command ran from the wrong directory or the import string is wrong. “Address already in use” means another process has the port; stop it or select `--port 8001`. “No module named fastapi” usually means the wrong Python environment.

Reference: [First steps](https://fastapi.tiangolo.com/tutorial/first-steps/) and [testing](https://fastapi.tiangolo.com/tutorial/testing/).
