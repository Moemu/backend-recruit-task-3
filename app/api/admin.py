from typing import Annotated

from deps.auth import check_and_get_current_role
from deps.sql import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User, UserRole
from repositories.user import UserRepository
from schemas.admin import RegisterRequestWithUsername, RegisterResponse
from services.auth_service import generate_random_password, get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
get_current_admin = check_and_get_current_role(role=UserRole.admin)


@router.post("/register", tags=["admin"])
async def register(
    request: RegisterRequestWithUsername,
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
    requests: list[RegisterRequestWithUsername],
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


@router.post("/edit", tags=["student"])
async def edit_info(
    request: RegisterRequestWithUsername,
    user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)

    await repo.edit_info(
        user=user,
        name=request.name,
        status=request.status,
        role=request.role,
        major=request.major,
        session=request.session,
        faculty=request.faculty,
        class_number=request.class_number,
    )

    return {"msg": "User updated successfully"}
