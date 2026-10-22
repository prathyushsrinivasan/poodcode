## Run a server database locally

Install Docker with Compose support and make sure the Docker engine is running. Copy the reference `compose.yaml` into your learning project; the command below needs that file in the current directory. It starts only PostgreSQL, binds port 5432 to localhost, and persists data in a named volume. Add a newly generated URL-safe local password as `POSTGRES_PASSWORD` in `.env`.

An **image** is a packaged runtime; a **container** is a running instance of it. Compose declares services to run together. A **volume** keeps database files outside the replaceable container. The host port connects your Python process to PostgreSQL; the service name `db` identifies the database inside a Compose network. Module 11 teaches building your own API image; here you only run a prebuilt database image.

```text
docker compose up -d db
docker compose ps
docker compose exec db pg_isready -U taskboard -d taskboard
```

Install `psycopg[binary]` and `alembic`. In `.env`, set:

```dotenv
DATABASE_URL=postgresql+psycopg://taskboard:YOUR_LOCAL_PASSWORD@localhost:5432/taskboard
```

Use a URL-safe generated local password, or percent-encode reserved characters in credentials. Restart the app after changing its connection URL. `localhost` works when Python runs on your host. If Python runs in a Compose service, use the database service name `db` instead.

Switching engines does not migrate existing SQLite rows. This lab intentionally starts a fresh PostgreSQL database. Real data migration needs an export/import plan and verification of IDs, counts, relationships and types.

**Ready to continue:** the readiness command reports accepting connections. To inspect rows use `docker compose exec db psql -U taskboard -d taskboard`; enter `\q` to exit psql. `docker compose stop db` stops the database, and `docker compose start db` restarts it. Keep the named volume; deleting a volume deletes its data.

## Give the schema a revision history

In your learning project run:

```text
python -m alembic init migrations
```

Replace the generated `migrations/env.py` with the following. Importing models registers the tables; the engine reads the same DATABASE_URL as the API. Leave Alembic's generated `script.py.mako` in place:

```python
from alembic import context
from app.db import Base, engine
from app import models

target_metadata = Base.metadata

if context.is_offline_mode():
    context.configure(url=engine.url, target_metadata=target_metadata,
                      literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata,
                          render_as_batch=engine.dialect.name == "sqlite",
                          compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
```

The reference already contains env.py and a baseline migration; when running that finished project, do not run `alembic init` or generate another initial revision. Run `upgrade head` against a fresh database instead. In your learning project, generate the first revision against the fresh PostgreSQL database before creating its tables, or Alembic will observe no schema difference.

```text
python -m alembic revision --autogenerate -m "create users and tasks"
python -m alembic upgrade head
python -m alembic current
python -m alembic check
```

Read the migration before applying it. Inspect table names, nullability, uniqueness, foreign keys, defaults and indexes. Autogenerate proposes changes; it cannot reliably infer a rename or your intended data backfill. Remove the earlier `create_all` setup from your startup flow. A release operation runs migrations once, rather than every worker trying to alter the schema at import time.

## Lab: evolve without losing a row

Seed a task. Add `description: Mapped[str | None]` to Task, generate a revision, inspect it, apply it and verify the original task remains. On a disposable database, rehearse downgrade and re-upgrade. Destructive downgrades are exercises for scratch databases, not an automatic recovery strategy for production data.

Reference: [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) and [autogeneration limitations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html).

<!-- lesson -->
## Bound the amount of work a client can ask for

This list-handler fragment replaces the local list implementation. Ownership is still a temporary seeded-user constant until module 7:

```python
from typing import Annotated
from fastapi import Query
from sqlalchemy import select

@router.get("", response_model=list[TaskRead])
def list_tasks(
    db: Db,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    done: bool | None = None,
):
    query = select(Task).where(Task.owner_id == 1)
    if done is not None:
        query = query.where(Task.done == done)
    return db.scalars(query.order_by(Task.id).offset(offset).limit(limit)).all()
```

Explicit ordering makes unchanged data predictable. Offset is easy to start with, but concurrent deletes/inserts can move page boundaries and large offsets can be expensive. A keyset alternative uses `Task.id > after_id` with the same owner constraint, stable ID ordering and a bounded limit. Return a next cursor based on the last returned item.

## Index for the query you actually run

The final model declares `Index("ix_tasks_owner_id_id", "owner_id", "id")`. Import `Index` from sqlalchemy and add `__table_args__ = (Index("ix_tasks_owner_id_id", "owner_id", "id"),)` inside Task, then generate and review its migration. The owner prefix narrows the user's rows while the ID supports ordered access. Every index consumes disk and write work; add indexes for observed queries, not every column.

In a PostgreSQL console, inspect:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title, done FROM tasks
WHERE owner_id = 1 ORDER BY id LIMIT 20;
```

On tiny tables a sequential scan can be the right plan. Seed realistic data before drawing performance conclusions. Watch total rows scanned, query duration and buffers; do not demand an index scan just because an index exists.

Relationships can also cause N+1 queries: loading a list of users and then each `user.tasks` lazily can issue one query per user. Use explicit queries or an appropriate eager-loading option such as `selectinload` when you truly need related collections. Our public task response avoids returning the owner relationship entirely.

## Lab: query and transaction drills

Create three tasks, mark one done and verify `?done=false`. Request `limit=0`, `limit=101` and `offset=-1`; expect 422. Add a keyset route in a practice branch and test that a new later ID does not shift the earlier cursor boundary.

For a two-row workflow, decide what must be atomic, modify both objects in the same Session, and commit once. Induce a failure and prove rollback leaves both unchanged. If two users can update the same shared row, investigate optimistic version checks or a transaction lock; a process-local Python lock does not coordinate multiple app instances.

Reference: [SQLAlchemy querying guide](https://docs.sqlalchemy.org/en/20/orm/queryguide/) and [PostgreSQL EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html).
