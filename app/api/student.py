from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.core.redis import get_redis_client
from app.deps.auth import check_and_get_current_role, oauth2_scheme
from app.deps.sql import get_db
from app.models.user import User, UserRole
from app.repositories.course import CourseRepository
from app.repositories.selection import SelectionRepository
from app.repositories.user import UserRepository
from app.services.auth_service import get_password_hash, verify_password

from .auth import logout

router = APIRouter()
check_and_get_current_student = check_and_get_current_role(UserRole.student)


@router.post("/info", tags=["student"])
async def get_info(
    current_user: Annotated[User, Depends(check_and_get_current_student)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到学生获取消息请求: {current_user.name}")
    current_user.password = ""  # Remove password from the response
    logger.info("获取消息请求处理成功")
    return current_user


@router.post("/edit", tags=["student"])
async def edit_info(
    user: Annotated[User, Depends(check_and_get_current_student)],
    name: Optional[str] = None,
    session: Optional[int] = None,
    dept_no: Optional[str] = None,
    major_no: Optional[str] = None,
    class_number: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到学生编辑消息请求: {user.name}")

    repo = UserRepository(db)
    await repo.edit_info(
        user=user,
        name=name,
        session=session,
        dept_no=dept_no,
        major_no=major_no,
        class_number=class_number,
    )

    logger.info("学生编辑消息请求处理成功")
    return {"msg": "User updated successfully"}


@router.post("/password", tags=["student"])
async def change_password(
    user: Annotated[User, Depends(check_and_get_current_student)],
    redis: Annotated[Redis, Depends(get_redis_client)],
    old_password: str,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    logger.info(f"收到学生编辑密码请求: {user.name}")

    if not verify_password(old_password, user.password):
        logger.warning("学生输入的原始密码有误，抛出 400")
        raise HTTPException(status_code=400, detail="Incorrect password")

    repo = UserRepository(db)
    await repo.change_password(user, get_password_hash(new_password))
    await logout(user, redis, token)

    logger.info("学生编辑密码请求成功，用户已登出")
    return {"msg": "Password updated successfully"}


@router.post("/schedule", tags=["student"])
async def get_schedule(
    term: str,
    current_user: Annotated[User, Depends(check_and_get_current_student)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到学生获取课程表请求: {current_user.name}")

    repo = UserRepository(db)
    schedule = await repo.get_schedule(current_user, term)
    if not schedule:
        logger.warning("该学生没课，查什么查，返回404")
        raise HTTPException(status_code=404, detail="Schedule not found")

    logger.info("学生获取课程表请求成功")
    return schedule


@router.post("/select", tags=["student"])
async def select_course(
    course_no: str,
    current_user: Annotated[User, Depends(check_and_get_current_student)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到学生选课请求: {current_user.name}, 课程编号: {course_no}")

    repo = SelectionRepository(db)
    selection = await repo.create_selection(current_user.id, course_no)

    logger.info("学生选课请求处理成功")
    return {"msg": "Course selected successfully", "selection_id": selection.id}


@router.post("/deselect", tags=["student"])
async def deselect_course(
    course_no: Optional[str] = None,
    selection_id: Optional[int] = None,
    current_user: User = Depends(check_and_get_current_student),
    db: AsyncSession = Depends(get_db),
):
    logger.info(
        f"收到学生退选请求: {current_user.name}, 课程编号: {course_no}, 选课ID: {selection_id}"
    )

    repo = SelectionRepository(db)

    if not course_no and not selection_id:
        logger.warning("学生退选请求缺少课程编号或选课ID，抛出 400")
        raise HTTPException(
            status_code=400, detail="Course No or selection ID must be provided"
        )

    if course_no:
        logger.info(f"收到学生退课请求: {current_user.name}, 课程编号: {course_no}")
        course = await CourseRepository(db).get_by_course_no(course_no)
        if not course:
            logger.warning(f"课程编号: {course_no} 不存在，抛出 404")
            raise HTTPException(status_code=404, detail="Course not found")

        selection = await repo.get_selection_by_student_and_course(
            current_user.id, course.id
        )
        if not selection:
            logger.warning(f"学生没有选中课程编号: {course_no}，抛出 404")
            raise HTTPException(status_code=404, detail="Selection not found")
        selection_id = selection.id

    if not selection_id:
        logger.warning("学生退选请求缺少选课ID，抛出 400")
        raise HTTPException(status_code=400, detail="Selection ID must be provided")

    repo = SelectionRepository(db)
    await repo.update_selection_status(selection_id, False)

    logger.info("学生退选请求处理成功")
    return {"msg": "Course deselected successfully"}


@router.post("/electives", tags=["student"])
async def get_elective_courses(
    term: str,
    current_user: Annotated[User, Depends(check_and_get_current_student)],
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"收到学生获取可选课程列表请求: {current_user.name}")

    repo = SelectionRepository(db)
    courses = await repo.get_available_courses(current_user.id, term)

    if not courses:
        logger.warning("该学生没有可选课程，返回空列表")
        return []

    logger.info("学生获取可选课程列表请求处理成功")
    return courses
