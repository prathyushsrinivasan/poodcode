## CORS is a browser policy

A frontend at a different origin needs permission to read API responses in a browser. An origin includes scheme, host and port. Use an explicit allowlist from validated settings:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-Request-ID"],
)
```

Set `CORS_ORIGINS=["https://your-frontend.example"]` as a JSON array in the environment. The middleware handles browser preflight OPTIONS. Test a permitted origin and an untrusted origin; only the permitted one should receive an allow-origin response header. CORS does not authenticate callers and does not block curl or server-to-server traffic.

## Complete the security boundary

Serve bearer credentials only over HTTPS outside localhost. Keep tokens out of URLs, logs, committed files and analytics. In a browser application, choose token/session storage deliberately. JavaScript-readable storage increases the impact of XSS; HttpOnly cookies reduce token access but require a deliberate SameSite/CSRF policy when automatically attached to requests.

Before opening registration to untrusted public traffic, add an abuse-control layer. Limit login attempts by more than just a user-supplied username, set expirations, cap key cardinality, and define 429 behavior with Retry-After. A gateway or Redis-backed implementation should share counters across workers. An in-memory dictionary resets on restart and is separate in each process.

Use a managed identity provider when you need account recovery, MFA and federation. Our local password/JWT example teaches primitives and object authorization; the complete account lifecycle is a larger system.

## Lab: write and test an enforcement policy

Choose a gateway or shared store in a practice environment. Configure a login burst and sustained limit, then send requests from two app workers and verify the combined threshold returns 429. Check the request just before the threshold, at the threshold, after expiry, and with two distinct accounts. Decide whether infrastructure failure should fail open or closed for your product; record the tradeoff.

For a minimal demonstration, document the limiter's interface with a fake shared store in unit tests before wiring the chosen infrastructure. The core reference does not include a distributed rate limiter; this milestone requires you to supply one or use the identity/gateway provider's enforced policy for a public deployment.

Reference: [CORS](https://fastapi.tiangolo.com/tutorial/cors/) and [OWASP API security](https://owasp.org/API-Security/).

<!-- lesson -->
## Measure requests without leaking credentials

Add middleware in `main.py` that generates its own request ID and logs method, route pattern, status and duration:

```python
import logging
from time import perf_counter
from uuid import uuid4
from fastapi import Request

log = logging.getLogger("uvicorn.error")

@app.middleware("http")
async def metrics(request: Request, call_next):
    request_id = uuid4().hex
    start = perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    route = request.scope.get("route")
    log.info("request_id=%s method=%s route=%s status=%s ms=%.1f",
             request_id, request.method, getattr(route, "path", "unmatched"),
             response.status_code, (perf_counter() - start) * 1000)
    return response
```

Using the route pattern avoids logging raw identifiers in the path. Do not log Authorization headers, passwords, request bodies or query strings. Unhandled exceptions still need server error reporting; this small middleware logs completed responses, while Uvicorn's error log records unhandled failures. Request IDs support investigation but are not authentication tokens.

## Separate process health from dependency health

```python
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

@app.get("/health/live")
def live():
    return {"status": "ok"}

@app.get("/health/ready")
def ready(db: Db):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(503, "Database unavailable")
    return {"status": "ready"}
```

Readiness here checks connectivity, not every application invariant or the migration version. Migrations must still be verified before release. Keep probes cheap and return no connection strings or stack traces. Set connection and gateway timeouts deliberately so a failing dependency cannot tie up all workers indefinitely.

## Lab: rehearse an outage

Using the local Compose database, stop only the database service. Check that readiness fails and liveness stays responsive, inspect logs, restart the database and verify recovery. In tests, override `get_db` with a stub whose execute raises an SQLAlchemy error; assert readiness returns 503 without relying on a real outage.

Record a small runbook: symptom, request ID, affected route, DB health, recent release, immediate mitigation and verification. Watch error rate, latency percentiles, connection-pool pressure and rejected logins. A useful alert asks for an action; a log line alone is not an alert.

**Checkpoint:** you can trace a failed request without exposing its credentials and distinguish an unhealthy process from an unavailable database.
