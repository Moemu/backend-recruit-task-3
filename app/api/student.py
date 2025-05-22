from typing import Annotated

from deps.auth import check_and_get_current_student, oauth2_scheme
from deps.sql import get_db
from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from repositories.user import UserRepository
from services.auth_service import get_password_hash, verify_password
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import logout

router = APIRouter()


@router.post("/info", tags=["student"])
async def get_info(
    current_user: Annotated[User, Depends(check_and_get_current_student)],
    db: AsyncSession = Depends(get_db),
):
    current_user.password = ""  # Remove password from the response
    return current_user


@router.post("/edit", tags=["student"])
async def edit_info(
    username: str,
    status: bool,
    major_id: int,
    grade: int,
    current_user: Annotated[User, Depends(check_and_get_current_student)],
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    user = await repo.get_by_name(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await repo.edit_info(
        user=user,
        username=username,
        status=status,
        major_id=major_id,
        grade=grade,
    )
    return {"msg": "User updated successfully"}


@router.post("/password", tags=["student"])
async def change_password(
    current_user: Annotated[User, Depends(check_and_get_current_student)],
    old_password: str,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    if not verify_password(old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    repo = UserRepository(db)
    user = await repo.get_by_name(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await repo.change_password(user, get_password_hash(new_password))
    await logout(current_user, token)

    return {"msg": "Password updated successfully"}


@router.post("/schedule", tags=["student"])
async def get_schedule(
    term: str,
    current_user: Annotated[User, Depends(check_and_get_current_student)],
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    schedule = await repo.get_schedule(current_user, term)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule
