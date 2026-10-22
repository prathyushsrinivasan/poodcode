## Async only helps when the work cooperates

Our reference deliberately uses synchronous SQLAlchemy sessions in `def` route functions. FastAPI runs ordinary sync route functions in a thread pool. Turning the signature into `async def` while keeping blocking database calls does not make those calls asynchronous.

Use `async def` for operations using awaitable libraries. A blocking call made directly inside an async function blocks the event loop. CPU-heavy work also needs separate process capacity or a job system; adding `await` syntax is not parallel computation.

This is a standalone concurrency lab, separate from Taskboard. Save as `async_lab.py`:

```python
import asyncio
from fastapi import FastAPI

app = FastAPI()

@app.get("/wait")
async def wait():
    await asyncio.sleep(0.2)
    return {"status": "done"}
```

Run `python -m uvicorn async_lab:app --port 8001`, then run this separate client:

```python
import asyncio
from time import perf_counter
import httpx

async def main():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8001") as client:
        start = perf_counter()
        responses = await asyncio.gather(*(client.get("/wait") for _ in range(5)))
        print([r.status_code for r in responses], perf_counter() - start)

asyncio.run(main())
```

Five waits can overlap. Replace the awaited sleep with `time.sleep(0.2)` and observe how latency changes under concurrent requests. Do not encode a precise wall-clock threshold in a flaky unit test; inspect the pattern and explain why it happens.

## Lab: choose the execution model

For each operation choose a strategy: a synchronous SQL query, an HTTPX async call, password hashing, and a CPU-heavy video encode. Keep sync SQL in sync handlers; await async network I/O; hash in an appropriate worker context; move sustained CPU-intensive jobs to independently supervised workers.

An async SQLAlchemy extension is possible, but requires an async engine, async driver, AsyncSession, awaited operations and one session per task. Do not share a single Session across concurrent `gather` operations.

Reference: [FastAPI concurrency](https://fastapi.tiangolo.com/async/) and [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html).

<!-- lesson -->
## Give shared resources a lifespan

Create `outbound_lab.py` as a standalone extension. It demonstrates a shared connection pool with bounded waits:

```python
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, HTTPException, Request

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient(timeout=httpx.Timeout(3.0)) as client:
        app.state.http = client
        yield

app = FastAPI(lifespan=lifespan)

@app.get("/upstream-health")
async def upstream_health(request: Request):
    try:
        response = await request.app.state.http.get("https://example.com/")
        response.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(504, "Upstream timed out")
    except httpx.HTTPError:
        raise HTTPException(502, "Upstream unavailable")
    return {"upstream_status": response.status_code}
```

The URL is fixed by the server. Accepting an arbitrary URL from a user introduces server-side request forgery risks; a real integration should constrain destinations and redirects. Avoid automatic retries for non-idempotent writes unless you have an idempotency strategy.

For tests, create an HTTPX client with `httpx.MockTransport` and replace `app.state.http` inside the TestClient lifespan context. The mock can return 200, return 500 or raise `httpx.ReadTimeout("slow")`. No real network call belongs in this unit test.

## Best-effort work versus durable jobs

```python
from fastapi import BackgroundTasks

def notify(task_id: int):
    # Lab only: replace with a best-effort notification adapter.
    print(f"Task {task_id} changed")

@app.post("/notification-demo", status_code=202)
def notification_demo(background: BackgroundTasks):
    background.add_task(notify, 123)
    return {"status": "accepted"}
```

BackgroundTasks runs after the response in the same app process. A crash can lose work. Do not hand it the request's database Session; if it needs a database, open a new session inside the task. A critical export, billing job or guaranteed notification needs persisted job state, retries, idempotency and worker monitoring. A transactional outbox can keep a database update and the record of work to publish atomic.

## Lab: simulate failure

Implement the mock upstream tests and assert 200, 504 and 502 respectively. Add the notification demo, then document what happens if the process exits before completion. Sketch a durable-job table and the state transitions pending → running → succeeded/failed, including retry limits and duplicate delivery handling.

**Stretch:** add a size-bounded file upload or authenticated WebSocket in a separate branch. Cover payload limits, authorization, disconnect cleanup and storage durability before treating it as part of the deployed API.

Reference: [Lifespan](https://fastapi.tiangolo.com/advanced/events/), [HTTPX transports](https://www.python-httpx.org/advanced/transports/), and [BackgroundTasks](https://fastapi.tiangolo.com/tutorial/background-tasks/).
