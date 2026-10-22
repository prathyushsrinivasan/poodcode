import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from . import auth, tasks
from .config import get_settings
from .db import Db

log = logging.getLogger("uvicorn.error")
app = FastAPI(title="Taskboard API", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=get_settings().cors_origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"], expose_headers=["X-Request-ID"],
)
app.include_router(auth.router)
app.include_router(tasks.router)


@app.middleware("http")
async def request_metrics(request: Request, call_next):
    request_id = uuid4().hex
    start = perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    # No bodies, credentials, tokens or query strings in this log.
    route = request.scope.get("route")
    log.info("request_id=%s method=%s route=%s status=%s ms=%.1f", request_id,
             request.method, getattr(route, "path", "unmatched"), response.status_code,
             (perf_counter() - start) * 1000)
    return response


@app.get("/health/live", tags=["health"])
def live():
    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
def ready(db: Db):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(503, "Database unavailable")
    return {"status": "ready"}
