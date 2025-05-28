from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.deps.auth import check_and_get_current_role
from app.deps.sql import get_db
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.admin import EditRequest, RegisterRequest, RegisterResponse
from app.services.auth_service import generate_random_password, get_password_hash

router = APIRouter()
get_current_admin = check_and_get_current_role(role=UserRole.admin)


@router.post("/register", tags=["admin"])
async def register(
    request: RegisterRequest,
    current_user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到注册请求: {request.name} 来自: {current_user.name}")

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
        logger.info("注册请求处理成功")
        return {
            "success": True,
            "msg": "User created successfully",
            "info": RegisterResponse(
                username=new_user.username, name=new_user.name, password=random_password
            ),
        }

    logger.warning(f"用户 {request.name} 已存在，抛出 400")
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
    logger.info(f"收到批量注册请求, 来自: {current_user.name}")

    repo = UserRepository(db)
    register_responses: list[RegisterResponse] = []

    for request in requests:
        logger.info(f"处理注册: {request.name} ...")
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
            logger.warning(f"用户 {request.name} 已存在，抛出 400")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

        register_responses.append(
            RegisterResponse(
                username=new_user.username, password=random_password, name=new_user.name
            )
        )

    logger.info("批量注册请求处理成功")
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
    logger.info(f"收到编辑用户请求: {request.name} 来自: {user.name}")

    repo = UserRepository(db)

    if not (target_user := await repo.get_by_name(request.username)):
        logger.warning(f"用户 {request.name} 不存在，抛出 404")
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

    logger.info("编辑用户请求处理成功")
    return {"msg": "User updated successfully"}


@router.delete("/delete", tags=["admin"])
async def delete_user(
    username: str,
    user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到删除用户请求: {username} 来自: {user.name}")

    repo = UserRepository(db)

    if not (target_user := await repo.get_by_name(username)):
        logger.warning(f"用户 {username} 不存在，抛出 404")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No such user.")

    await repo.delete_user(target_user)

    logger.info("删除用户请求处理成功")
    return {"msg": "User deleted successfully"}


@router.post("/info", tags=["admin"])
async def get_user_info(
    username: str,
    user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到获取用户信息请求: {username} 来自: {user.name}")
    repo = UserRepository(db)

    if not (target_user := await repo.get_by_name(username)):
        logger.warning(f"用户 {username} 不存在，抛出 404")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No such user.")

    target_user.password = ""

    logger.info("获取用户信息请求处理成功")
    return target_user
