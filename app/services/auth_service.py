from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from core.config import config
from models.user import User
from passlib.context import CryptContext
from repositories.user import UserRepository
from schemas.auth import Payload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    payload: Payload, expires_delta: Optional[timedelta] = None
) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    payload.exp = int(expire.timestamp())
    return jwt.encode(payload.to_json(), config.secret_key, algorithm=config.algorithm)


async def authenticate_user(
    userdb: UserRepository, username: str, password: str
) -> Optional[User]:
    user = await userdb.get_by_name(username)
    if user and verify_password(password, user.password):
        return user
    return None
