## A bearer token is a credential

Install `PyJWT`. The token subject identifies the user; it does not contain a password. A signed JWT is ordinarily readable, so keep its payload minimal. Use a cryptographically random server secret, short expiry and an explicit verification policy.

Add to `security.py`:

```python
from datetime import datetime, timedelta, timezone
import jwt
from .config import get_settings

def create_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    settings = get_settings()
    return jwt.encode(
        {"sub": str(user_id), "iat": now,
         "exp": now + timedelta(minutes=15),
         "iss": "taskboard", "aud": "taskboard-api"},
        settings.jwt_secret.get_secret_value(), algorithm="HS256",
    )
```

Now connect the module 6 credential check to tokens. In `schemas.py` add:

```python
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

In `auth.py`, import Token from schemas and create_token from security. Rename `login_check` to `login`, replace its decorator with `@router.post("/token", response_model=Token)`, and replace its final `return user` with `return Token(access_token=create_token(user.id))`. Keep password verification and no-store headers. Remove the temporary `/login-check` route after its replacement passes tests. No later handler should trust a prior successful credential check without a token.

Next resolve users in a dependency in `security.py`:

```python
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .db import Db
from .models import User

oauth2 = OAuth2PasswordBearer(tokenUrl="auth/token")

def bad_credentials():
    return HTTPException(401, "Invalid credentials",
                         headers={"WWW-Authenticate": "Bearer"})

def current_user(token: Annotated[str, Depends(oauth2)], db: Db):
    try:
        payload = jwt.decode(
            token, get_settings().jwt_secret.get_secret_value(),
            algorithms=["HS256"], audience="taskboard-api", issuer="taskboard",
            options={"require": ["sub", "exp", "iat", "iss", "aud"]},
        )
        user_id = int(payload["sub"])
        if user_id < 1:
            raise ValueError("invalid subject")
    except (jwt.InvalidTokenError, ValueError, TypeError, KeyError):
        raise bad_credentials()
    user = db.get(User, user_id)
    if user is None or not user.active:
        raise bad_credentials()
    return user

CurrentUser = Annotated[User, Depends(current_user)]
```

`OAuth2PasswordBearer` extracts a bearer credential and advertises the security scheme in OpenAPI. It does not itself verify a JWT or implement user authorization. The dependency verifies the signature and claims, then checks current database state so disabled users lose access.

## Lab: attack your verifier

Test a missing bearer credential, garbage, a valid token, an expired token, the wrong signing secret, a wrong audience, missing expiry and a nonnumeric subject. Expect 401 for every invalid token. Decode a token without verification in a throwaway inspection script to see its readable fields; never use an unverified payload to authorize a request.

Reference: [FastAPI JWT security](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) and [PyJWT claim validation](https://pyjwt.readthedocs.io/en/stable/usage.html).

<!-- lesson -->
## Scope every operation to the authenticated user

Replace the temporary `owner_id=1` stage with a real identity. Add `user: CurrentUser` to create/list/read/patch/delete routes, and set a newly created task's `owner_id=user.id`. Do not accept owner IDs in the create or patch schema.

Centralize the single-resource lookup in `tasks.py`:

```python
def owned_task(task_id: int, db, user_id: int):
    task = db.scalar(select(Task).where(
        Task.id == task_id, Task.owner_id == user_id
    ))
    if task is None:
        raise HTTPException(404, "Task not found")
    return task

@router.get("/{task_id}", response_model=TaskRead)
def read_task(task_id: int, db: Db, user: CurrentUser):
    return owned_task(task_id, db, user.id)
```

Use this lookup before PATCH and DELETE too. In the list route, start from `select(Task).where(Task.owner_id == user.id)` before applying filters, ordering and pagination. Filtering a Python list after fetching everybody's rows is wasteful and can leak data through pagination behavior.

This API returns 404 for both nonexistent and unowned tasks so it does not advertise another user's resource IDs. A role-protected administrative route can instead return 403 for an authenticated user without the needed permission. A missing/invalid credential remains 401.

## Lab: prove object isolation

Create Alice and Bob, log in as each, and let Alice create a task. Bob's list must exclude it. Bob's GET, PATCH and DELETE of its ID must return 404. After all three attempts, Alice must still read the unchanged task. Submit `owner_id` in a body and confirm 422 rather than ownership reassignment.

Also update the earlier task tests: obtain a token with a registration/login helper and pass its Authorization header to every protected request. Keep separate tests asserting that anonymous requests now fail with 401. Expecting the old anonymous success after adding authentication would test the wrong contract.

## Extension: a role policy

On a practice branch, add a server-managed `is_admin` Boolean with a default of false, a reviewed migration, and a test-only way to provision an admin directly in the fixture. Never include this flag in public registration input. Then write a dependency:

```python
def require_admin(user: CurrentUser):
    if not user.is_admin:
        raise HTTPException(403, "Administrator required")
    return user

# On a new administrative router:
# dependencies=[Depends(require_admin)]
```

Test no token → 401, normal user → 403, admin → success, and public signup with `is_admin=true` → 422. This extension is intentionally separate from the core reference. More complex collaboration needs membership and permission models, not a growing pile of special-case flags.

**Checkpoint:** having a valid JWT is not enough to access an arbitrary object. You must show that each query enforces the relevant permission.
