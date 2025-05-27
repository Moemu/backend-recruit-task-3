from typing import Annotated

from deps.auth import check_and_get_current_role
from deps.sql import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User, UserRole
from repositories.user import UserRepository
from schemas.admin import EditRequest, RegisterRequest, RegisterResponse
from services.auth_service import generate_random_password, get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
get_current_admin = check_and_get_current_role(role=UserRole.admin)


@router.post("/register", tags=["admin"])
async def register(
    request: RegisterRequest,
    current_user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    random_password = generate_random_password()
    hash_password = get_password_hash(random_password)

    if new_user := await repo.create_user(
        name=request.name,
        password=hash_password,
        session=request.session,
        faculty=request.faculty,
        major=request.major,
        class_number=request.class_number,
        role=request.role,
    ):
        return {
            "success": True,
            "msg": "User created successfully",
            "info": RegisterResponse(
                username=new_user.username, name=new_user.name, password=random_password
            ),
        }

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="User already exists",
    )


@router.post("/batch_register", tags=["admin"])
async def batch_register(
    requests: list[RegisterRequest],
    current_user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    register_responses: list[RegisterResponse] = []

    for request in requests:
        random_password = generate_random_password()
        hash_password = get_password_hash(random_password)
        if not (
            new_user := await repo.create_user(
                name=request.name,
                password=hash_password,
                session=request.session,
                faculty=request.faculty,
                major=request.major,
                class_number=request.class_number,
                role=request.role,
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )
        register_responses.append(
            RegisterResponse(
                username=new_user.username, password=random_password, name=new_user.name
            )
        )

    return {
        "success": True,
        "msg": "Users created successfully",
        "infos": register_responses,
    }


@router.post("/edit", tags=["admin"])
async def edit_info(
    request: EditRequest,
    user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)

    if not (target_user := await repo.get_by_name(request.username)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No such user.")

    await repo.edit_info(
        user=target_user,
        name=request.name,
        status=request.status,
        role=request.role,
        major=request.major,
        session=request.session,
        faculty=request.faculty,
        class_number=request.class_number,
    )

    return {"msg": "User updated successfully"}


@router.delete("/delete", tags=["admin"])
async def delete_user(
    username: str,
    user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)

    if not (target_user := await repo.get_by_name(username)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No such user.")

    await repo.delete_user(target_user)

    return {"msg": "User deleted successfully"}


@router.post("/info", tags=["admin"])
async def get_user_info(
    username: str,
    user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)

    if not (target_user := await repo.get_by_name(username)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No such user.")

    target_user.password = ""

    return target_user
