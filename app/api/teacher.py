from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.deps.auth import check_and_get_current_role
from app.deps.sql import get_db
from app.models.user import User, UserRole
from app.repositories.course import CourseRepository
from app.schemas.course import CourseCreateRequest, CourseUpdateRequest

router = APIRouter()
check_and_get_current_teacher = check_and_get_current_role(role=UserRole.teacher)


@router.post("/add", tags=["course"])
async def add_course(
    course: CourseCreateRequest,
    current_user: Annotated[User, Depends(check_and_get_current_teacher)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到教师添加课程({course.course_name})请求: {current_user.name}")

    repo = CourseRepository(db)
    result = await repo.create_course(
        course_name=course.course_name,
        teacher_id=current_user.id,
        major_no=course.major_no,
        session=course.session,
        course_type=course.course_type,
        course_date=course.course_date,
        credit=course.credit,
        is_public=course.is_public,
    )

    logger.info(f"教师添加课程({course.course_name})请求成功")
    return {"msg": "Course created successfully", "course_no": result.course_no}


@router.post("/info", tags=["course"])
async def get_course_info(
    course_no: str,
    current_user: Annotated[User, Depends(check_and_get_current_teacher)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到教师获取课程消息请求: {current_user.name}")

    repo = CourseRepository(db)
    course = await repo.get_by_course_no(course_no)
    if not course:
        logger.warning(f"课程: {course_no} 不存在，返回 404")
        raise HTTPException(status_code=404, detail="Course not found")

    logger.info("教师获取课程消息请求成功")
    return course


@router.post("/edit", tags=["course"])
async def edit_course(
    course: CourseUpdateRequest,
    current_user: Annotated[User, Depends(check_and_get_current_teacher)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到教师编辑课程消息请求: {current_user.name}")

    repo = CourseRepository(db)
    result = await repo.edit_course(
        course_no=course.course_no,
        course_name=course.course_name,
        teacher=current_user.id,
        major_no=course.major_no,
        session=course.session,
        course_type=course.course_type,
        course_date=course.course_date,
        credit=course.credit,
        is_public=course.is_public,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Incorrect course_no",
        )

    logger.info("教师编辑课程消息请求成功")
    return {"msg": "Course updated successfully", "course_no": result.course_no}


@router.delete("/delete", tags=["course"])
async def delete_course(
    course_no: str,
    current_user: Annotated[User, Depends(check_and_get_current_teacher)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到教师删除课程请求: {current_user.name}")

    repo = CourseRepository(db)
    if not await repo.delete_course(course_no):
        logger.warning(f"课程: {course_no} 不存在，返回 404")
        raise HTTPException(
            status_code=404,
            detail="Incorrect course_no",
        )

    logger.info("教师删除课程请求成功")
    return {"msg": "Course deleted successfully"}


@router.post("/status", tags=["course"])
async def set_course_status(
    course_no: str,
    status: int,
    current_user: Annotated[User, Depends(check_and_get_current_teacher)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到教师申请修改课程状态请求: {current_user.name}")

    repo = CourseRepository(db)
    if not await repo.set_status(course_no, status):
        logger.warning(f"课程: {course_no} 不存在，返回 404")
        raise HTTPException(
            status_code=404,
            detail="Incorrect course_no",
        )

    logger.warning(
        "教师申请修改课程状态请求成功，由于申请接口未实现，已自动修改目标状态"
    )
    return {"msg": "Course status updated successfully"}
