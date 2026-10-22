## Choose a concrete first cloud deployment

This course uses Render as a first deployment target: a Python web service plus managed PostgreSQL. The Docker image also makes the API portable to other container platforms. You need your own Git repository, a cloud account and a suitable service/database plan. Inspect current pricing and supported features before provisioning; provider plans and pre-deploy availability can change.

Push your learning API to a repository you control, excluding `.env`, local databases and virtual environments. For this monorepo reference, the service root directory is `examples/fastapi-taskboard`; for a standalone learning repo it is the repository root.

## Deployment procedure

1. Create managed PostgreSQL in the same region as the web service. Keep the service's database connection on the provider's internal network when available.
2. Create a Python web service connected to your repository. Select Python 3.12 using the provider's supported runtime configuration.
3. Set the build command to `pip install -r requirements.txt`.
4. Set the start command to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. `$PORT` is expanded by the cloud shell, not a literal string to put inside Docker's JSON CMD.
5. Configure `DATABASE_URL`, a fresh random `JWT_SECRET`, and JSON `CORS_ORIGINS` in the provider's secret/environment settings. Convert the managed URL's scheme to `postgresql+psycopg://` for our chosen driver; retain its credentials, host, path and required TLS options.
6. Configure one pre-deploy command `python -m alembic upgrade head` on a plan that supports it. If unavailable, use a single controlled one-off release job with database access before starting the new version. Do not start multiple migration jobs in workers.
7. Set the health-check path to `/health/ready`, enable the appropriate login abuse controls from module 10, and deploy. Verify the public URL uses HTTPS.

The native web-service start command differs from the local Dockerfile's fixed port. If deploying the image instead, configure its runtime command to use the platform's required port. Trusted proxy settings must match the provider's documented proxy topology before relying on forwarded client IPs or schemes; do not trust arbitrary forwarded headers from public callers.

## Lab: smoke-test the public behavior

Register Alice and Bob, log in using form data, create a task as Alice and read it back. As Bob, list tasks and try to read, patch and delete Alice's task. Verify all isolation assertions. Never paste live tokens into source files or issue trackers.

The reference `scripts/cloud_smoke.py` automates this against `API_BASE_URL`. It creates two throwaway accounts and deletes its task; run only against a deployment you control. Check `GET /health/ready`, then redeploy the service and verify a separately created persistent task is still present. Restarting an app instance must not erase managed database rows.

From the reference directory with development dependencies installed:

```powershell
$env:API_BASE_URL = "https://YOUR-SERVICE.onrender.com"
python scripts/cloud_smoke.py
```

Expect `Cloud smoke passed`. This tests actual HTTP requests; it does not create your cloud service or supply its secrets. The two throwaway usernames remain so remove them using an authorized maintenance procedure if desired.

**Debugging:** an unhealthy deploy often comes from the wrong import path/root directory, missing secret, unrun migration, unreachable database, wrong driver scheme, incorrect port or a missing dependency. Use service logs and readiness, without printing secrets. Confirm the build and migration revision rather than repeatedly clicking redeploy.

References: [Render FastAPI deployment](https://render.com/docs/deploy-fastapi), [PostgreSQL connections](https://render.com/docs/postgresql-creating-connecting), [pre-deploy commands](https://render.com/docs/deploys#pre-deploy-command), and [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/).

<!-- lesson -->
## Final practical: build without the walkthrough

Start from an empty repository. Keep the endpoint contract and acceptance rubric visible, but close the reference code. Build and deploy a Taskboard API with:

| Capability | Required evidence |
|---|---|
| Design | App package, routers, request/output schemas, dependency boundaries, OpenAPI contract |
| Database | PostgreSQL persistence, constraints, session lifetime, bounded queries, reviewed Alembic history |
| Security | Argon2, short-lived verified JWTs, disabled-user rejection, object ownership on every route, input/output allowlists |
| Testing | Isolated API tests, invalid inputs, token failures, two-user isolation, PostgreSQL migrations and smoke checks |
| Cloud | HTTPS deployment, injected secrets, readiness, logs without credentials, a task surviving redeploy |
| Operations | A written release/rollback plan and a backup restored into a scratch database |

Treat the security and persistence items as mandatory. A high quiz score does not compensate for one user's access to another user's task. Complete the final build only when every acceptance check passes; this app records self-reported completion, not a security audit or an automated deployment certificate.

## Make recovery concrete

For an application rollback, record the current image/commit and database revision, deploy a deliberately broken non-destructive app revision in a practice environment, restore the previous app revision and rerun health plus authentication checks. The database schema must remain compatible with that older app. Rolling back code does not undo destructive schema changes.

For database recovery, use the provider's supported backup/export tools or `pg_dump`. Restore into a **new, disposable database**, point a practice instance at it and read a known seeded task. Record the backup time, restore duration and verification query. Never rehearse a restore over the only copy of your live data.

Use expand/backfill/contract for changes that would otherwise break existing rows or old app versions: add a compatible field, backfill data, ship readers/writers, then enforce stricter constraints in a later coordinated release. Prove this on a scratch database before putting it in a release plan.

## Lab: transfer the design to due dates

Implement a nullable timezone-aware due date with validation, a migration and a filter for overdue unfinished tasks. Decide how clients represent UTC timestamps, how omitted PATCH fields differ from null, and which index supports the new query. Test boundaries around time zones and completed tasks. Deploy the change while preserving existing rows and show that the prior compatible app still starts.

Start by testing this independent input model:

```python
from pydantic import AwareDatetime, BaseModel

class DueDateInput(BaseModel):
    due_at: AwareDatetime | None = None

def test_due_date_contract():
    value = DueDateInput(due_at="2030-01-02T12:00:00+09:00")
    assert value.due_at.utcoffset().total_seconds() == 9 * 3600
    assert DueDateInput().due_at is None
```

Add a test that a timezone-naive timestamp is rejected, then decide whether null clears a due date in PATCH. That differs from the existing non-null title/done policy: do not copy the old validator unchanged. Store a timezone-aware timestamp in PostgreSQL and compare it with an explicitly controlled UTC clock in tests.

## Defend your design in five minutes

Explain the request path from HTTP input through validation, identity, ownership, session and transaction to public response. Show the test that would catch a missing ownership filter. Explain why sync SQL routes use `def`, why a JWT is not encrypted, why `create_all` is not your migration plan, and why the database survives a redeploy.

Revisit the project after a week and rebuild one route from memory. Then add a different small API—bookmarks, inventory or expenses—with the same engineering constraints. Competence is being able to carry the patterns into a new problem, debug it and operate it.

**Completion:** the four original outcomes are demonstrated by an app you designed, a real database you can evolve, endpoints you can defend with tests, and a cloud release you can verify and recover.
