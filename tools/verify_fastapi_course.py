"""Parse all Python fences; optionally execute cumulative beginner checkpoints.

Run --run-checkpoints in the reference virtual environment. All generated files
and databases belong to temporary directories; no live database is contacted.
"""
import argparse
import ast
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
checked = 0
lessons = {}
for path in sorted((root / "src/data/fastapi").glob("[0-9]*.md")):
    content = path.read_text(encoding="utf-8")
    lessons[path.name[:2]] = []
    for number, match in enumerate(re.finditer(r"^```python\r?\n(.*?)^```", content, re.M | re.S), 1):
        ast.parse(match.group(1), filename=f"{path.name}:block-{number}")
        lessons[path.name[:2]].append(match.group(1))
        checked += 1
print(f"Parsed {checked} Python lesson blocks successfully.")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--run-checkpoints", action="store_true")
args = parser.parse_args()
if not args.run_checkpoints:
    raise SystemExit(0)


def block(module, contains):
    return next(source for source in lessons[module] if contains in source)


def run_stage(name, files, assertions):
    with tempfile.TemporaryDirectory(prefix="poodcode-fastapi-checkpoint-") as directory:
        target = Path(directory).resolve()
        # TemporaryDirectory owns this exact target; verify it stays in TEMP.
        target.relative_to(Path(tempfile.gettempdir()).resolve())
        for relative, source in files.items():
            destination = (target / relative).resolve()
            destination.relative_to(target)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(source, encoding="utf-8")
        env = {**os.environ, "DATABASE_URL": "sqlite:///./checkpoint.sqlite",
               "JWT_SECRET": "checkpoint-only-secret-" + "x" * 40,
               "CORS_ORIGINS": "[]", "PYTHONPATH": "", "PYTHONDONTWRITEBYTECODE": "1"}
        subprocess.run([sys.executable, "-c", assertions], cwd=target, env=env, check=True)
    print(f"Passed checkpoint: {name}")


first_app = block("01", '@app.get("/health/live")')
run_stage("first endpoint", {"app/__init__.py": "", "app/main.py": first_app}, '''
from fastapi.testclient import TestClient
from app.main import app
with TestClient(app) as client:
    assert client.get("/hello?name=Ada").json() == {"message": "Hello, Ada"}
    assert client.get("/health/live").status_code == 200
    assert client.post("/hello").status_code == 405
''')

schemas = block("02", "class TaskCreate") + "\n" + block("02", "class TaskPatch")
main = block("02", "app = FastAPI()") + "\nfrom .schemas import TaskPatch\n" + block("02", "def list_tasks(")
crud_assertions = '''
from fastapi.testclient import TestClient
from app.main import app
with TestClient(app) as client:
    created = client.post("/tasks", json={"title": "  Ship  "})
    assert created.status_code == 201
    path = f'/tasks/{created.json()["id"]}'
    assert created.json()["title"] == "Ship"
    assert client.patch(path, json={"done": True}).json()["done"] is True
    assert client.patch(path, json={"done": False}).json()["done"] is False
    assert client.patch(path, json={"title": None}).status_code == 422
    assert client.post("/tasks", json={"title": " "}).status_code == 422
    assert client.post("/tasks", json={"title": "ok", "owner_id": 1}).status_code == 422
    assert client.get("/tasks?limit=0").status_code == 422
    result = client.delete(path)
    assert result.status_code == 204 and result.content == b""
    assert client.get(path).status_code == 404
'''
run_stage("in-memory CRUD and PATCH", {
    "app/__init__.py": "", "app/schemas.py": schemas, "app/main.py": main,
}, crud_assertions)

tasks = main.replace("app = FastAPI()", 'router = APIRouter(prefix="/tasks", tags=["tasks"])')
tasks = "from fastapi import APIRouter\n" + tasks.replace("@app.", "@router.")
tasks = tasks.replace('("/tasks"', '(""').replace('("/tasks/{task_id}"', '("/{task_id}"')
run_stage("router refactor preserves the HTTP contract", {
    "app/__init__.py": "", "app/schemas.py": schemas, "app/tasks.py": tasks,
    "app/main.py": block("03", "app.include_router(tasks_router)"),
}, crud_assertions)

run_stage("dependency override", {
    "dependency_demo.py": block("03", "def get_prefix()"),
}, block("03", "app.dependency_overrides[get_prefix]"))
run_stage("SQL rows, bound parameters and rollback", {}, block("04", "import sqlite3"))

orm_schemas = schemas.replace("class TaskRead(BaseModel):", "class TaskRead(BaseModel):\n    model_config = ConfigDict(from_attributes=True)")
orm_schemas += "\n" + block("06", "Username = Annotated[")
passwords = block("06", "PasswordHash.recommended()")
registration = block("06", 'router = APIRouter(prefix="/auth"')
login = block("06", "def login_check(")
db_crud = block("04", "def create_task(")
files = {
    "app/__init__.py": "", "app/config.py": block("03", "class Settings(BaseSettings)"),
    "app/db.py": block("04", "class Base(DeclarativeBase)"),
    "app/models.py": block("04", "class User(Base)"), "app/schemas.py": orm_schemas,
    "app/security.py": passwords, "app/auth.py": registration + "\n" + login,
    "app/tasks.py": 'from fastapi import APIRouter\nrouter = APIRouter(prefix="/tasks")\n' + db_crud,
    "app/main.py": block("03", "app.include_router(tasks_router)") + "\nfrom .auth import router as auth_router\napp.include_router(auth_router)\n",
}
run_stage("registration and credential check before JWTs", files, '''
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine
Base.metadata.create_all(engine)
with TestClient(app) as client:
    body = {"username": "Alice", "password": "correct-horse-battery"}
    response = client.post("/auth/register", json=body)
    assert response.status_code == 201 and set(response.json()) == {"id", "username"}
    assert client.post("/auth/register", json=body).status_code == 409
    result = client.post("/auth/login-check", data=body)
    assert result.status_code == 200 and result.json()["username"] == "alice"
    assert result.headers["cache-control"] == "no-store"
    assert client.post("/auth/login-check", data={**body, "password": "wrong-password"}).status_code == 401
    assert client.post("/auth/login-check", data={**body, "username": "unknown"}).status_code == 401
    assert client.post("/auth/login-check", json=body).status_code == 422
''')

files["app/security.py"] = passwords + "\n" + block("07", "def create_token(") + "\n" + block("07", "def current_user(")
files["app/schemas.py"] += "\n" + block("07", "class Token(BaseModel)")
token_login = login.replace('@router.post("/login-check", response_model=UserRead)', '@router.post("/token", response_model=Token)')
token_login = token_login.replace("def login_check(", "def login(").replace("    return user", "    return Token(access_token=create_token(user.id))")
files["app/auth.py"] = registration + "\nfrom .schemas import Token\nfrom .security import create_token\n" + token_login
create_task = db_crud.split('\n@router.get')[0].replace("def create_task(body: TaskCreate, db: Db):", "def create_task(body: TaskCreate, db: Db, user: CurrentUser):").replace("owner_id=1", "owner_id=user.id")
files["app/tasks.py"] = 'from fastapi import APIRouter\nfrom .security import CurrentUser\nrouter = APIRouter(prefix="/tasks")\n' + create_task + "\n" + block("07", "def owned_task(")
run_stage("JWT transition and owned detail lookup", files, '''
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine
Base.metadata.create_all(engine)
with TestClient(app) as client:
    headers = []
    for username in ["alice", "bob"]:
        body = {"username": username, "password": "correct-horse-battery"}
        assert client.post("/auth/register", json=body).status_code == 201
        token = client.post("/auth/token", data=body)
        assert token.status_code == 200
        headers.append({"Authorization": "Bearer " + token.json()["access_token"]})
    created = client.post("/tasks", headers=headers[0], json={"title": "Private"})
    assert created.status_code == 201
    path = f'/tasks/{created.json()["id"]}'
    assert client.get(path, headers=headers[0]).status_code == 200
    assert client.get(path, headers=headers[1]).status_code == 404
    assert client.get(path).status_code == 401
    assert client.post("/auth/login-check").status_code == 404
''')
