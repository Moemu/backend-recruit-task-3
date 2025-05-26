from typing import Annotated, Optional

from deps.auth import check_and_get_current_role, oauth2_scheme
from deps.sql import get_db
from fastapi import APIRouter, Depends, HTTPException
from models.user import User, UserRole
from repositories.user import UserRepository
from services.auth_service import get_password_hash, verify_password
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import logout

router = APIRouter()
check_and_get_current_student = check_and_get_current_role(UserRole.student)


@router.post("/info", tags=["student"])
async def get_info(
    current_user: Annotated[User, Depends(check_and_get_current_student)],
    db: AsyncSession = Depends(get_db),
):
    current_user.password = ""  # Remove password from the response
    return current_user


@router.post("/edit", tags=["student"])
async def edit_info(
    user: Annotated[User, Depends(check_and_get_current_student)],
    name: Optional[str] = None,
    session: Optional[int] = None,
    faculty: Optional[int] = None,
    major: Optional[int] = None,
    class_number: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await repo.edit_info(
        user=user,
        name=name,
        session=session,
        faculty=faculty,
        major=major,
        class_number=class_number,
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
