## A container packages the runtime

The completed reference lives in `examples/fastapi-taskboard`. Run these commands from that directory. `requirements.txt` pins the direct dependencies used in verification; its `.in` companion records update ranges. For a stricter release process, generate and review a complete transitive lock with hashes for your target environment as well.

```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home learner
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini .
USER learner
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

The dependency layer comes before changing application code to improve build caching. Exec-form CMD lets the server receive process signals. Bind to `0.0.0.0` inside the container. Keep `--reload` out of deployment. A non-root process reduces what a compromised app can modify; it does not replace the application's security controls.

The supplied `.dockerignore` excludes `.env`, virtual environments, local databases and caches. Never COPY secrets into an image and hope deleting them in a later layer removes them from image history.

## Build and run locally

```text
docker build -t taskboard:course .
```

Use an untracked `.env.docker` containing a new JWT_SECRET and your PostgreSQL connection URL. When PostgreSQL runs in the supplied Compose network, the host is `db` rather than localhost. Find the actual network name using `docker network ls` (usually `fastapi-taskboard_default`). Then run, replacing NETWORK with that name:

```text
docker run --rm --network NETWORK --env-file .env.docker taskboard:course python -m alembic upgrade head
docker run --rm --network NETWORK --env-file .env.docker -p 8000:8000 taskboard:course
```

The first command is a one-off migration operation. The second starts the server. An alternative is a hosted/host-accessible PostgreSQL URL; ensure its hostname is reachable from inside the container. Native Docker networking varies by platform, so verify connectivity rather than assuming localhost refers to your host.

## Lab: inspect the artifact

Call `/health/ready`, register and create a task, stop the API container and run a new one. The task must remain in PostgreSQL. Verify the process runs as `learner` and no `.env` was copied into `/srv`. Check the server exits cleanly on docker stop.

Reference: [FastAPI in Docker](https://fastapi.tiangolo.com/deployment/docker/) and [Docker build practices](https://docs.docker.com/build/building/best-practices/).

<!-- lesson -->
## CI should reject behavior regressions

The repository supplies a CI template at `examples/fastapi-taskboard/ci/fastapi-course.yml`. Copy it to `.github/workflows/fastapi-course.yml` in your learning repository to enable it; publishing an active workflow requires suitable GitHub workflow permissions. Once installed, it runs the API tests, starts a disposable PostgreSQL service, applies migrations, checks metadata drift and runs a database-backed smoke script. It runs against Python 3.12 and 3.14 so the container's Python baseline and the local verification runtime are both covered.

When creating your separate learning repository, copy the workflow and adjust its working directory if the Python project is at the repository root. The essential sequence is:

```text
python -m pip install -r requirements-dev.txt
python -m pytest -q
# DATABASE_URL now points at a disposable PostgreSQL database:
python -m alembic upgrade head
python -m alembic check
python scripts/smoke.py
```

The test module intentionally sets its own SQLite URL; migrations and the smoke script are separate Python processes and use the PostgreSQL URL from the workflow environment. This keeps fast tests isolated while checking the real schema and driver too.

## Release sequence

Use a repeatable sequence: tests pass → image/build prepared → compatible migration reviewed → one migration job succeeds → new app serves → health and authenticated smoke checks pass. Configure deployment to wait for passing CI checks or trigger releases manually after the checks pass.

Multiple workers multiply database pools. A large per-process pool times many workers can exhaust the database's connection budget. Start with a modest worker count, measure real traffic and choose a total connection budget deliberately. Local dictionaries, caches and rate limits are also per process unless backed by shared infrastructure.

## Lab: make CI earn its place

Push a temporary branch with the owner filter deliberately removed. The ownership test should fail in CI. Restore the filter and verify the workflow passes. Add a harmless schema change on a disposable branch and confirm `alembic check` fails until you create the corresponding migration.

Write down which exact code revision and database revision you intend to deploy. A green test badge does not identify the artifact currently running in production unless the release process connects them.

**Checkpoint:** a clean machine can reproduce the checks, and a broken authorization change cannot silently pass the release gate.
