import time
from datetime import timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.deps.auth import get_current_user, get_db, oauth2_scheme
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import Payload
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
)
from app.services.token_blacklist import add_token_to_blacklist

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
    return {"access_token": access_token, "token_type": "bearer"}


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
