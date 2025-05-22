from datetime import datetime
from typing import Annotated

import jwt
from core.config import config
from deps.sql import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from models.user import User, UserRole
from repositories.user import UserRepository
from schemas.auth import Payload
from services.token_blacklist import is_token_blacklisted
from sqlalchemy.ext.asyncio import AsyncSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="./login")


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload_dict = jwt.decode(
            token, config.secret_key, algorithms=[config.algorithm]
        )
        payload = Payload(**payload_dict)
        if (
            (payload.sub is None or payload.exp is None)
            or payload.exp < datetime.timestamp(datetime.now())
            or await is_token_blacklisted(payload.jti)
        ):
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    repo = UserRepository(db)
    user = await repo.get_by_name(payload.sub)
    if not user or not user.status:
        raise credentials_exception
    return user


async def check_and_get_current_teacher(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    user = await get_current_user(db, token)
    if user.role == UserRole.student:
        raise HTTPException(status_code=403, detail="Permission denied")
    return user


async def check_and_get_current_student(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    user = await get_current_user(db, token)
    if user.role != UserRole.student:
        raise HTTPException(status_code=403, detail="Permission denied")
    return user
