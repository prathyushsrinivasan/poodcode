from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .db import Db
from .models import User
from .schemas import Token, UserCreate, UserRead
from .security import CurrentUser, create_token, credentials_error, dummy_hash, password_hash

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


@router.post("/token", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: Db, response: Response):
    # The form dependency has no length constraints of its own.
    if len(form.username) > 50 or not 12 <= len(form.password) <= 128:
        raise credentials_error()
    user = db.scalar(select(User).where(User.username == form.username.strip().lower()))
    valid = password_hash.verify(form.password, user.password_hash if user else dummy_hash)
    if not valid or user is None or not user.active:
        raise credentials_error()
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return Token(access_token=create_token(user.id))


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser):
    return user
