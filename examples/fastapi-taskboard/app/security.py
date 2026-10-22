from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from .config import get_settings
from .db import Db
from .models import User

password_hash = PasswordHash.recommended()
# Avoid a fast exit for unknown usernames on the login path.
dummy_hash = password_hash.hash("dummy-password-that-is-never-a-login")
oauth2 = OAuth2PasswordBearer(tokenUrl="auth/token")


def credentials_error() -> HTTPException:
    return HTTPException(401, "Invalid credentials", headers={"WWW-Authenticate": "Bearer"})


def create_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    settings = get_settings()
    return jwt.encode(
        {"sub": str(user_id), "iat": now, "exp": now + timedelta(minutes=settings.token_minutes),
         "iss": "taskboard", "aud": "taskboard-api"},
        settings.jwt_secret.get_secret_value(), algorithm="HS256",
    )


def current_user(token: Annotated[str, Depends(oauth2)], db: Db) -> User:
    try:
        payload = jwt.decode(
            token, get_settings().jwt_secret.get_secret_value(), algorithms=["HS256"],
            audience="taskboard-api", issuer="taskboard",
            options={"require": ["sub", "exp", "iat", "iss", "aud"]},
        )
        user_id = int(payload["sub"])
        if user_id < 1:
            raise ValueError("invalid subject")
    except (jwt.InvalidTokenError, ValueError, TypeError, KeyError):
        raise credentials_error()
    user = db.get(User, user_id)
    if user is None or not user.active:
        raise credentials_error()
    return user


CurrentUser = Annotated[User, Depends(current_user)]
