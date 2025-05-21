from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from core.config import config
from deps import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from models.user import User, UserRole
from passlib.context import CryptContext
from repositories.user import UserRepository
from services.token_blacklist import is_token_blacklisted
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Payload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="./login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码有效性

    :param plain_password: 尝试登录的密码明文
    :param hashed_password: 已落库的哈希密码
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    """
    获得密码哈希

    :param password: 密码明文
    """
    return pwd_context.hash(password)


def create_access_token(
    payload: Payload, expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建通行密钥

    :param payload: jwt payload
    :param expires_delta: 通行密钥过期时间

    :return: encoded_jwt
    """
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    payload.exp = int(expire.timestamp())
    encoded_jwt = jwt.encode(
        payload.to_json(), config.secret_key, algorithm=config.algorithm
    )
    return encoded_jwt


async def authenticate_user(
    userdb: UserRepository, username: str, password: str
) -> Optional[User]:
    """
    认证用户, 失败返回 None

    :param userdb: UserRepository 实例
    :param username: 用户名
    :param password: 明文密码
    """
    if not (user := await userdb.get_by_name(username)):
        return None
    if not verify_password(password, user.password):
        return None

    return user


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """
    获取当前登录用户信息

    :param userdb: AsyncSession 实例
    :param token: Bearer token
    """
    repo = UserRepository(db)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 核验密钥有效性
    try:
        payload_dict = jwt.decode(
            token, config.secret_key, algorithms=[config.algorithm]
        )
        payload = Payload(**payload_dict)
        username = payload.sub
        if (
            (payload.sub is None or payload.exp is None)
            or payload.exp < datetime.timestamp(datetime.now())
            or await is_token_blacklisted(payload.jti)
        ):
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    # 核验用户是否存在
    if not (user := await repo.get_by_name(username)):
        raise credentials_exception
    # 核验用户状态是否有效
    if not user.status:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


async def check_and_get_current_teacher(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """
    检查并获取当前登录的教师账号

    :param userdb: AsyncSession 实例
    :param token: Bearer token
    """
    user = await get_current_user(db, token)
    if user.role == UserRole.student:
        raise HTTPException(status_code=403, detail="Permission denied")
    return user


async def check_and_get_current_student(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """
    检查并获取当前登录的学生账号

    :param userdb: AsyncSession 实例
    :param token: Bearer token
    """
    user = await get_current_user(db, token)
    if user.role != UserRole.student:
        raise HTTPException(status_code=403, detail="Permission denied")
    return user
