## A password should never become a response field

Install `pwdlib[argon2]` and `python-multipart`. Use an adaptive password hash with a salt. Do not store plaintext, reversible encryption, or a fast unsalted general-purpose digest as the password representation.

In `security.py` start with:

```python
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
dummy_hash = password_hash.hash("dummy-password-that-is-never-a-login")
```

Add registration and output schemas in `schemas.py`. Normalize before validating the allowed character pattern; otherwise uppercase input can be rejected before the lowercase conversion runs.

```python
from typing import Annotated
from pydantic import BeforeValidator, Field, StringConstraints

Username = Annotated[
    str, StringConstraints(pattern=r"^[a-z0-9_]{3,50}$"),
    BeforeValidator(lambda v: v.strip().lower() if isinstance(v, str) else v),
]

class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: Username
    password: str = Field(min_length=12, max_length=128)

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
```

The password policy here is a course choice, not a substitute for compromised-password checks, account recovery or MFA. Never silently strip or lowercase passwords. Public registration input has no role or owner field.

Create `auth.py` and include its router in `main.py`:

```python
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from .db import Db
from .models import User
from .schemas import UserCreate, UserRead
from .security import password_hash

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=201)
def register(body: UserCreate, db: Db):
    user = User(username=body.username, password_hash=password_hash.hash(body.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Username unavailable")
    return user
```

Registration can reveal username availability through 409; that is an explicit product choice for this username-based API. Login failures will use a generic response. Higher-privacy account systems may choose a different registration flow.

## Lab: hash, verify and filter

Register an account, inspect the database hash, and call `password_hash.verify` with the right and wrong passwords. Confirm the JSON response contains only ID and username. Register `ALICE` after `alice` and expect 409, then register a different user and prove recovery after rollback.

Reference: [FastAPI password hashing and JWT tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) and [pwdlib guide](https://frankie567.github.io/pwdlib/guide/).

<!-- lesson -->
## Login accepts a form, registration accepts JSON

First build a complete credential check that needs no JWT code. Add the following to `auth.py`, using `OAuth2PasswordRequestForm`: send `username` and `password` as form fields. This temporary route returns the public user when credentials are valid; it does not create a session or authenticate any later request. Module 7 replaces it with the token route after implementing token creation.

```python
from typing import Annotated
from fastapi import Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from .security import dummy_hash

def bad_credentials():
    return HTTPException(401, "Invalid credentials",
                         headers={"WWW-Authenticate": "Bearer"})

@router.post("/login-check", response_model=UserRead)
def login_check(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: Db,
                response: Response):
    if len(form.username) > 50 or not 12 <= len(form.password) <= 128:
        raise bad_credentials()
    user = db.scalar(select(User).where(
        User.username == form.username.strip().lower()
    ))
    valid = password_hash.verify(form.password,
                                 user.password_hash if user else dummy_hash)
    if not valid or user is None or not user.active:
        raise bad_credentials()
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return user
```

The dummy hash avoids skipping the expensive verification step for an unknown username. Generic detail prevents an obvious account-enumeration response. Neither makes the route immune to timing analysis or abuse: rate limits and monitoring arrive in module 10.

Do not log `form`, the password or any later token. At this stage `/auth/login-check` returns only the same public fields as registration, with Cache-Control: no-store. Test that independently before moving on. The final reference contains `/auth/token` rather than this temporary teaching route.

## Understand the teaching boundary

This is a first-party username/password login exercise using FastAPI's form and bearer helpers. It is not a complete OAuth authorization server. For browser/mobile sign-in, federation or third-party clients, prefer an established OpenID Connect provider and authorization code with PKCE. Validate that provider's tokens against its issuer, audience and keys. Our reference intentionally omits refresh-token rotation, email recovery, MFA and account verification; add these deliberately or delegate identity to a provider.

## Lab: failures are part of the contract

Write tests for correct login, wrong password, unknown user, disabled user and an overlong form field. The credential failures should all return 401 with a generic detail and bearer challenge. A JSON body sent to the form-based route should fail validation rather than accidentally succeed.

Call `/auth/login-check` in these module 6 tests. A correct login returns ID and username without any password fields; it does not yet return a bearer token. In module 7 update the helper to call `/auth/token` and use its access token for subsequent requests.

**Checkpoint:** you can explain why input validation, password verification, token issuance and authorization are four separate steps. Never interpret a client-supplied username as proof of identity.
