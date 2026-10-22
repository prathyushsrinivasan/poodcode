# Taskboard: FastAPI course reference

This is the complete worked solution for **Courses → FastAPI Course** in
Poodcode. Start the course at `/fastapi-course` and build your own version before
comparing with this directory. It is a separate Python application: it does not
change Poodcode's Rust backend or store course progress in its database.

The reference implements registration, form login, short-lived JWTs, private task
CRUD, bounded pagination, SQLAlchemy 2, SQLite/PostgreSQL, Alembic migrations,
request IDs, readiness/liveness and API tests. The course adds separate async
integration, administrator-policy and distributed rate-limit labs. The core
reference does not implement a full identity/account-recovery system or a
distributed rate limiter; complete the relevant lab or use a provider's enforced
controls before opening registration to untrusted traffic.

## Run locally

Use Python 3.12+ and run all commands from this directory. Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Replace JWT_SECRET in `.env` with the generated value. The example value is a
placeholder, not a deployment secret. Then:

```powershell
.venv\Scripts\python.exe -m alembic upgrade head
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

On macOS/Linux use `python3 -m venv .venv`, `cp .env.example .env`, and
`.venv/bin/python` in place of `.venv\Scripts\python.exe`. Once activated,
`python` can replace either explicit path.

Open <http://127.0.0.1:8000/docs>. Register a username and password (12–128
characters). Choose **Authorize**, enter those credentials and leave client ID
and secret empty. Create a task. Use a second account to check isolation.

| Method | Path | Behavior |
|---|---|---|
| POST | `/auth/register` | JSON username/password → public user, 201 |
| POST | `/auth/token` | Form username/password → access token, 200 |
| GET | `/auth/me` | Authenticated public user |
| POST | `/tasks` | JSON title → private task, 201 |
| GET | `/tasks?limit=20&offset=0&done=false` | Owned tasks, stable ID order |
| GET | `/tasks/{id}` | Owned task or 404 |
| PATCH | `/tasks/{id}` | Optional title/done; omitted unchanged, null rejected |
| DELETE | `/tasks/{id}` | Owned task deletion, empty 204 |
| GET | `/health/live` | Process liveness |
| GET | `/health/ready` | Database connectivity, 503 on failure |

Task input does not accept owner_id. User output does not include password_hash.
Invalid inputs return 422; invalid/missing credentials return 401; duplicate
usernames return 409. Ownership failures return 404. Empty PATCH is a no-op.

## Verify

```text
python -m pytest -q
python -m alembic check
python scripts/smoke.py
```

Tests create a fresh in-memory SQLite database per test and override the session
dependency. They intentionally set test-only environment values before app
imports. The smoke script uses the configured database after migrations and
creates two throwaway accounts; its task is deleted. Do not run it against a
database where creating test accounts is unwanted.

Direct dependencies are pinned in `requirements.txt`; `requirements.in` records
the supported update ranges. Transitive dependencies are resolver-selected, so
this is not a full hash-locked environment. Review dependency updates and produce
a complete target-platform lock if your release process requires one.

## PostgreSQL

Install Docker with Compose. Add a generated URL-safe POSTGRES_PASSWORD to `.env`:

```text
docker compose up -d db
docker compose ps
```

Change DATABASE_URL in `.env` to
`postgresql+psycopg://taskboard:YOUR_PASSWORD@localhost:5432/taskboard`, then run
`python -m alembic upgrade head`, `python -m alembic check`, and
`python scripts/smoke.py`. Changing the URL selects a new database; it does not
transfer previous SQLite rows. A named volume retains PostgreSQL data when the
database container restarts.

When editing models, generate a candidate with
`python -m alembic revision --autogenerate -m "describe change"`, review it,
then apply. The included migration template supports future revisions.

## Container and CI

`docker build -t taskboard:course .` builds the non-root API image. Inject secrets
at runtime with an untracked env file. Use a PostgreSQL URL reachable from inside
the container; localhost there means the container itself. When joining the
Compose network use hostname `db`. Run migrations once using the same image
before starting the API. See module 11 for full commands.

[The CI template](ci/fastapi-course.yml), once installed, runs the HTTP suite,
migrations, metadata-drift check and real PostgreSQL smoke on Python 3.12/3.14.
Copy it to `.github/workflows/fastapi-course.yml` in your learning repository,
adjusting working directories if needed. It is supplied as a template rather
than an active workflow; publishing an active GitHub workflow requires workflow
permission on your GitHub credentials. PostgreSQL and Docker require their own
runtime checks; a passing SQLite suite
does not establish those results.

## Cloud deployment

Module 12 walks through Render web service + managed PostgreSQL. Use this
directory as the root for this monorepo. Set Python 3.12, build with
`pip install -r requirements.txt`, and start with
`uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Set a new JWT_SECRET and a
`postgresql+psycopg://` DATABASE_URL using the managed database's internal host.
Preserve connection parameters and provider-required TLS settings.

Run `python -m alembic upgrade head` as a single pre-deploy/release operation,
then serve the app. Availability of pre-deploy hooks depends on the provider's
current plan. Configure `/health/ready`, explicit CORS origins, appropriate login
abuse controls and HTTPS. Do not use the local SQLite file as cloud persistence.

With development dependencies installed, smoke-test only a service you own:

```powershell
$env:API_BASE_URL = "https://YOUR-SERVICE.onrender.com"
python scripts/cloud_smoke.py
```

The smoke creates two throwaway accounts. Separately create a task, redeploy and
read it again to prove persistence. Rehearse app rollback with a compatible schema
and restore a database backup into a separate scratch database. The course does
not create cloud resources or incur charges automatically.

Official references: [FastAPI](https://fastapi.tiangolo.com/tutorial/),
[SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/),
[Alembic](https://alembic.sqlalchemy.org/en/latest/),
[Render deployment](https://render.com/docs/deploy-fastapi).
