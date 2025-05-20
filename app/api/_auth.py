from datetime import datetime, timedelta, timezone
from typing import Optional, Union

import jwt
from core.config import config
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from repositories.user_repository import UserRepository

from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="./token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
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
    if not (user := await userdb.get_by_name(username)):
        return None
    if not verify_password(password, user.password):
        return None

    return user
