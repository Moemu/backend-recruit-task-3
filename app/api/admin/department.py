from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.deps.auth import check_and_get_current_role
from app.deps.sql import get_db
from app.models.user import User, UserRole
from app.repositories.department import DepartmentRepository

router = APIRouter()
get_current_admin = check_and_get_current_role(role=UserRole.admin)


@router.post("/add", tags=["admin", "department"])
async def add_department(
    dept_name: str,
    current_user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到添加院系请求: {dept_name} 来自: {current_user.name}")

    repo = DepartmentRepository(db)
    department = await repo.create_department(dept_name)

    logger.info(f"添加院系({department.dept_name})请求成功")
    return {"msg": "Department created successfully", "dept_no": department.dept_no}


@router.post("/edit", tags=["admin", "department"])
async def edit_department(
    dept_no: str,
    dept_name: str,
    current_user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到编辑院系请求: {dept_name} 来自: {current_user.name}")

    repo = DepartmentRepository(db)
    department = await repo.edit_department(dept_no, dept_name)

    if not department:
        logger.warning(f"院系: {dept_no} 不存在，返回 404")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )

    logger.info(f"编辑院系({department.dept_name})请求成功")
    return {"msg": "Department updated successfully", "dept_no": department.dept_no}


@router.post("/info", tags=["admin", "department"])
async def get_department_info(
    dept_no: str,
    current_user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到获取院系信息请求: {dept_no} 来自: {current_user.name}")

    repo = DepartmentRepository(db)
    department = await repo.get_by_dept_no(dept_no)

    if not department:
        logger.warning(f"院系: {dept_no} 不存在，返回 404")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )

    logger.info("获取院系信息请求成功")
    return department


@router.delete("/delete", tags=["admin", "department"])
async def delete_department(
    dept_no: str,
    current_user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到删除院系请求: {dept_no} 来自: {current_user.name}")

    repo = DepartmentRepository(db)
    success = await repo.delete_department(dept_no)

    if not success:
        logger.warning(f"院系: {dept_no} 不存在，返回 404")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )

    logger.info(f"删除院系({dept_no})请求成功")
    return {"msg": "Department deleted successfully"}
