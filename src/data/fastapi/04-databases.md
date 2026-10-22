## Read rows and SQL before introducing an ORM

A database table stores rows with named columns. A primary key identifies a row. A foreign key points to a related row; a unique constraint prevents duplicate values. SQL reads and changes these rows. SQLAlchemy will construct SQL for us, but you should first see what the database actually does.

Save this independent exercise as `sql_bridge.py`. It uses Python's built-in SQLite support and does not touch your app's database:

```python
import sqlite3

with sqlite3.connect(":memory:") as connection:
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL)")
    connection.execute("""CREATE TABLE tasks (
        id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL,
        owner_id INTEGER NOT NULL REFERENCES users(id)
    )""")
    connection.execute("INSERT INTO users (id, username) VALUES (?, ?)", (1, "alice"))
    connection.execute("INSERT INTO tasks VALUES (?, ?, ?, ?)", (1, "Learn SQL", 0, 1))
    connection.commit()
    rows = connection.execute(
        "SELECT title FROM tasks WHERE owner_id = ? ORDER BY id LIMIT ?", (1, 20)
    ).fetchall()
    assert rows == [("Learn SQL",)]
    connection.execute("UPDATE tasks SET done = ? WHERE id = ?", (1, 1))
    connection.rollback()
    assert connection.execute("SELECT done FROM tasks WHERE id = 1").fetchone()[0] == 0
```

`SELECT` reads, `INSERT` creates, `UPDATE` changes and `DELETE` removes rows. `WHERE` selects which rows are affected. `commit` makes a transaction's changes durable; `rollback` discards its uncommitted changes. Placeholder parameters pass values separately from SQL syntax, which protects against SQL injection.

**Warm-up lab:** change the username, add a second task, filter unfinished tasks and deliberately insert a duplicate username. Explain why a dictionary cannot provide a database's uniqueness and transaction guarantees across multiple app processes.

## Model data and invariants

Install `sqlalchemy`. A task belongs to one user; a user can own many tasks. Start with `id`, `username`, `password_hash`, and `active` on users, and `id`, `title`, `done`, `owner_id` on tasks. Password handling arrives in module 6; for this local database lab, seed a test user directly and label its password hash unusable.

Create `app/db.py`:

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from .config import get_settings

class Base(DeclarativeBase):
    pass

url = get_settings().database_url
engine = create_engine(
    url,
    connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
    pool_pre_ping=True,
)
if url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

SessionLocal = sessionmaker(engine, expire_on_commit=False)

def get_db():
    with SessionLocal() as session:
        yield session

Db = Annotated[Session, Depends(get_db)]
```

The engine manages connections. A Session tracks objects and a transaction. It is mutable state scoped to one unit of work: do not share a global Session across concurrent requests. Closing a session releases resources and rolls back uncommitted work. SQLite's thread option lets the connection cross the request thread boundary; it does not make a Session safe to share.

Create `app/models.py` using SQLAlchemy 2 annotations:

```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(default=True)
    tasks: Mapped[list["Task"]] = relationship(back_populates="owner")

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    done: Mapped[bool] = mapped_column(default=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped[User] = relationship(back_populates="tasks")
```

`ForeignKey` enforces relational integrity. `relationship` provides Python navigation between objects; it is not the constraint. Database uniqueness protects against concurrent duplicate usernames. Pydantic validates HTTP input while SQL constraints protect data regardless of how a write reaches the database.

## Lab: create and inspect

For this local stage only, run `python -c "from app import models; from app.db import Base, engine; Base.metadata.create_all(engine)"`. Importing models registers metadata before creation. Then create `seed_local.py` in the learning project root:

```python
from sqlalchemy import select
from app.db import SessionLocal
from app.models import User

with SessionLocal() as session:
    user = session.scalar(select(User).where(User.username == "local_seed"))
    if user is None:
        user = User(username="local_seed", password_hash="unusable-local-lab-value")
        session.add(user)
        session.commit()
    print(f"Local teaching owner ID: {user.id}")
```

Run `python seed_local.py`. The first user in a fresh learning database normally has ID 1; if the printed ID differs, use that ID in this module's temporary owner constant. This script is repeatable without inserting duplicate usernames. It is only a local teaching seed and must not be used as a login account. Module 6 creates real accounts with password hashes, and module 7 removes the fixed owner entirely. After switching to a fresh PostgreSQL database in module 5, run the seed there after migrations if you are still using the temporary owner.

Insert a task referencing the seeded user, query it after restarting Python and try an invalid owner ID to confirm the foreign key fails.

Reference: [SQLAlchemy ORM quick start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html) and [session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html).

<!-- lesson -->
## Replace storage without replacing the contract

Add `model_config = ConfigDict(from_attributes=True)` to `TaskRead` so the response model can read ORM attributes. In `tasks.py`, replace the dictionary routes with session-backed routes. For this module only, set `owner_id` to the ID of your seeded local test user. This is a temporary local-only stage: module 7 replaces it with the authenticated user before deployment.

```python
from fastapi import HTTPException
from sqlalchemy import select
from .db import Db
from .models import Task
from .schemas import TaskCreate, TaskRead

@router.post("", response_model=TaskRead, status_code=201)
def create_task(body: TaskCreate, db: Db):
    task = Task(title=body.title, owner_id=1)  # local seeded-user stage only
    db.add(task)
    db.commit()
    return task

@router.get("/{task_id}", response_model=TaskRead)
def read_task(task_id: int, db: Db):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(404, "Task not found")
    return task
```

For PATCH, load the row, apply `body.model_dump(exclude_unset=True)`, and commit. For DELETE, load, delete, commit and return an empty 204 response. For list, use `db.scalars(select(Task).order_by(Task.id).limit(20)).all()`. Database IDs replace the teaching counter.

Do not call a FastAPI handler such as `read_task(task_id)` from another handler after adding `db: Db`: a plain Python call does not inject that argument. Pass the session explicitly (`read_task(task_id, db)`), or preferably extract `get_task_or_404(task_id, db)` as an ordinary helper and call that from GET/PATCH/DELETE. The helper has no Depends defaults and accepts normal Python values. This same pattern becomes `owned_task` in module 7.

## Keep tests isolated as soon as persistence appears

Move the `client` fixture from `tests/test_tasks.py` into `tests/conftest.py`, replacing dictionary resets with this setup. Keep test functions in `test_tasks.py` and let pytest inject the fixture. Conftest loads before test modules so the test configuration is set before the app creates its engine:

```python
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "test-only-secret-" + "x" * 40

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.db import Base, get_db
from app.main import app
from app.models import User

@pytest.fixture
def client():
    engine = create_engine("sqlite://", poolclass=StaticPool,
                           connect_args={"check_same_thread": False})
    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(User(id=1, username="local_seed", password_hash="unusable-test-value"))
        session.commit()
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

This is provided scaffolding for now: a fresh database and seeded owner per test, one connection visible to request threads, and cleanup after the test. There is no shared `main.tasks` dictionary anymore. Module 8 revisits the fixture in depth; once routes require authentication, replace the fixed teaching seed with the registration/login helpers and send the returned Authorization header in task tests. The old anonymous task assertions must then deliberately expect 401.

## Transactions define what succeeds together

```python
from sqlalchemy.exc import IntegrityError

try:
    db.add(new_user)
    db.commit()
except IntegrityError:
    db.rollback()
    raise HTTPException(409, "Username unavailable")
```

This fragment belongs in a registration handler; `new_user` is the row prepared by that handler. A single-row operation can commit at the route boundary. A workflow creating multiple related rows should commit once after all its invariants pass, so partial success does not escape. Do not commit independently in each helper when the caller needs atomicity.

Bound expressions such as `User.username == submitted_name` keep data separate from SQL syntax. If raw SQL is needed, use `text("... WHERE username = :name")` with a bound parameter dictionary, never an f-string containing user input.

## Lab: durability and rollback

Create a task over HTTP, stop Uvicorn, restart it and read the task. Trigger a unique-username violation in a Session, roll back, then successfully insert a different username. Write a transaction that inserts two rows and intentionally fails before commit; assert neither row survives.

**Debugging:** “no such table” means metadata/migrations did not run against the configured database. Relative SQLite paths depend on the working directory. “PendingRollbackError” usually means an earlier failed operation was caught without rolling back.

**Checkpoint:** the HTTP contract still works, persistence survives restart, and you can draw request → session → transaction → engine → database.
