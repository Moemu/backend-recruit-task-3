from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from core.config import config
from deps import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from models.user import User
from passlib.context import CryptContext
from repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

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


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建通行密钥

    :param data: jwt payload
    :param expires_delta: 通行密钥过期时间

    :return: encoded_jwt
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)
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
    :param token: oauth2_scheme 表单
    """
    repo = UserRepository(db)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    if not (user := await repo.get_by_name(username)):
        raise credentials_exception
    if user.status == 1:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user
