import time
from datetime import timedelta
from typing import Annotated, Optional

import jwt
from core.config import config
from deps import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.user import User, UserRole
from repositories.user import UserRepository
from services.token_blacklist import add_token_to_blacklist
from sqlalchemy.ext.asyncio import AsyncSession

from ._auth import (  # get_current_user,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    oauth2_scheme,
)
from .models import Payload, Token

router = APIRouter()


@router.post("/login", tags=["auth"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    user = await authenticate_user(repo, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.expire_minutes)
    access_token = create_access_token(
        payload=Payload(sub=user.username), expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout", tags=["auth"])
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    token: str = Depends(oauth2_scheme),
):
    payload = jwt.decode(token, config.secret_key, algorithms=config.algorithm)
    jti = payload.get("jti")
    exp = payload.get("exp")
    now = int(time.time())
    ttl = exp - now
    await add_token_to_blacklist(jti, ttl)
    return {"msg": "Logged out"}


@router.post("/register", tags=["auth"])
async def register(
    session: int,
    faculty: int,
    major: Optional[int] = None,
    class_number: Optional[int] = None,
    role: UserRole = UserRole.student,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    hash_password = get_password_hash(form_data.password)
    if await repo.create_user(
        username=form_data.username,
        password=hash_password,
        session=session,
        faculty=faculty,
        major=major,
        class_number=class_number,
        role=role,
    ):
        return {"success": True, "msg": "User created successfully"}

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="User already exists",
    )
