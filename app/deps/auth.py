from datetime import datetime
from typing import Annotated, Callable, Coroutine

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.redis import get_redis_client
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.auth import Payload
from app.services.token_blacklist import is_token_blacklisted

from .sql import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="./login")


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
    redis: Annotated[Redis, Depends(get_redis_client)],
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
            or await is_token_blacklisted(redis, payload.jti)
        ):
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    repo = UserRepository(db)
    user = await repo.get_by_name(payload.sub)
    if not user or not user.status:
        raise credentials_exception
    return user


def check_and_get_current_role(
    role: UserRole,
) -> Callable[..., Coroutine[None, None, User]]:
    async def wrapper(
        db: Annotated[AsyncSession, Depends(get_db)],
        token: Annotated[str, Depends(oauth2_scheme)],
        redis: Annotated[Redis, Depends(get_redis_client)],
    ) -> User:
        user = await get_current_user(db, token, redis)
        if user.role != role:
            raise HTTPException(status_code=403, detail="Permission denied")
        return user

    return wrapper
