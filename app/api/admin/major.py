from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.deps.auth import check_and_get_current_role
from app.deps.sql import get_db
from app.models.user import User, UserRole
from app.repositories.major import MajorRepository

router = APIRouter()
get_current_admin = check_and_get_current_role(role=UserRole.admin)


@router.post("/add", tags=["admin", "major"])
async def add_major(
    major_name: str,
    dept_no: str,
    current_user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到添加专业请求: {major_name} 来自: {current_user.name}")

    repo = MajorRepository(db)
    major = await repo.create_major(major_name, dept_no)

    if not major:
        logger.warning(f"院系编号: {dept_no} 不存在，返回 404")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="dept_no is invalid"
        )

    logger.info(f"添加专业({major.major_name})请求成功")
    return {"msg": "Major created successfully", "major_no": major.major_no}


@router.post("/edit", tags=["admin", "major"])
async def edit_major(
    major_no: str,
    major_name: Optional[str] = None,
    dept_no: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到编辑专业请求: {major_name} 来自: {current_user.name}")

    repo = MajorRepository(db)
    major = await repo.edit_major(major_no, major_name, dept_no)

    if not major:
        logger.warning(f"专业(院系): {major_no}({dept_no}) 不存在，返回 404")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Major not found or dept_no is invalid.",
        )

    logger.info(f"编辑专业({major.major_name})请求成功")
    return {"msg": "Major updated successfully", "major_no": major.major_no}


@router.post("/info", tags=["admin", "major"])
async def get_major_info(
    major_no: str,
    current_user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到获取专业信息请求: {major_no} 来自: {current_user.name}")

    repo = MajorRepository(db)
    major = await repo.get_by_major_no(major_no)

    if not major:
        logger.warning(f"专业: {major_no} 不存在，返回 404")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Major not found"
        )

    logger.info("获取专业信息请求成功")
    return major


@router.delete("/delete", tags=["admin", "major"])
async def delete_major(
    major_no: str,
    current_user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到删除专业请求: {major_no} 来自: {current_user.name}")

    repo = MajorRepository(db)
    if not await repo.delete_major(major_no):
        logger.warning(f"专业: {major_no} 不存在，返回 404")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Major not found"
        )

    logger.info(f"删除专业({major_no})请求成功")
    return {"msg": "Major deleted successfully"}
