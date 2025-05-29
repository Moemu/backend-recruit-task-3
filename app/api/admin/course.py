from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.deps.auth import check_and_get_current_role
from app.deps.sql import get_db
from app.models.user import User, UserRole
from app.repositories.course import CourseRepository

router = APIRouter()
get_current_admin = check_and_get_current_role(role=UserRole.admin)


@router.post("/set_status", tags=["admin", "course"])
async def set_course_status(
    course_no: str,
    status: int,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到管理员设置课程状态请求: {course_no} 来自: {current_user.name}")

    repo = CourseRepository(db)
    course = await repo.set_course_status(course_no, status, reason)

    logger.info(f"管理员设置课程({course.course_name})状态请求成功")
    return {"msg": "Course status updated successfully", "course_no": course.course_no}


@router.post("/get_pending", tags=["admin", "course"])
async def get_pending_courses(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到管理员获取待审核课程请求: 来自: {current_user.name}")

    repo = CourseRepository(db)
    pending_courses = await repo.get_pending_courses()

    if not pending_courses:
        logger.warning("没有待审核的课程")
        raise HTTPException(status_code=404, detail="No pending courses found")

    logger.info("管理员获取待审核课程请求成功")
    return pending_courses
