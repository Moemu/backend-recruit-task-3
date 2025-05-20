from datetime import timedelta
from typing import Annotated

from core.config import config
from deps import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

from ._auth import authenticate_user, create_access_token, oauth2_scheme
from .models import Token

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
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout", tags=["auth"])
async def logout(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"success": True}
