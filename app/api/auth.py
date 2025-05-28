import time
from datetime import timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.logger import logger
from app.core.redis import get_redis_client
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
    logger.info(f"收到登录请求: {form_data.username}")

    repo = UserRepository(db)
    user = await authenticate_user(repo, form_data.username, form_data.password)

    if not user:
        logger.warning(f"用户 {form_data.username} 不存在或密码错误，抛出 401")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(f"为用户 {form_data.username} 创建 access_token ...")
    access_token_expires = timedelta(minutes=config.expire_minutes)
    access_token = create_access_token(
        payload=Payload(sub=user.username), expires_delta=access_token_expires
    )

    logger.info(f"用户 {form_data.username} 登录成功, 密钥后五位 {access_token[-5:]}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", tags=["auth"])
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    redis: Annotated[Redis, Depends(get_redis_client)],
    token: str = Depends(oauth2_scheme),
):
    logger.info(f"收到登出请求: {current_user.name}")

    payload = jwt.decode(token, config.secret_key, algorithms=config.algorithm)
    jti = payload.get("jti")
    exp = payload.get("exp")
    now = int(time.time())
    ttl = exp - now

    logger.debug(f"将 jti {jti[-5:]} 加入到 redis 黑名单中...")
    await add_token_to_blacklist(redis, jti, ttl)

    logger.info(f"用户 {current_user.name} 登出成功，jti 已禁用")
    return {"msg": "Logged out"}
