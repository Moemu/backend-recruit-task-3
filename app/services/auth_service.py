from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from passlib import pwd
from passlib.context import CryptContext

from app.core.config import config
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import Payload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码有效性

    :param plain_password: 目标检测的明文密码
    :param hashed_password: 数据库中的哈希密码
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    获得密码哈希
    """
    return pwd_context.hash(password)


def create_access_token(
    payload: Payload, expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建 JWT 通行密钥

    :param payload: jwt payload
    :parm expires_delta: 过期时间，默认15分钟
    """
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    payload.exp = int(expire.timestamp())
    return jwt.encode(payload.to_json(), config.secret_key, algorithm=config.algorithm)


async def authenticate_user(
    userdb: UserRepository, username: str, password: str
) -> Optional[User]:
    """
    登录用户鉴权
    """
    user = await userdb.get_by_name(username)
    if user and verify_password(password, user.password):
        return user
    return None


def generate_random_password(length: int = 8) -> str:
    """
    随机生成一个密码
    """
    return pwd.genword(length=length, charset="ascii_62")
