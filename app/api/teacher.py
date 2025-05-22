from typing import Annotated

from api._auth import check_and_get_current_teacher
from deps import get_db
from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from repositories.course import CourseRepository
from sqlalchemy.ext.asyncio import AsyncSession

from .models import CourseCreateRequest, CourseUpdateRequest

router = APIRouter()


@router.post("/add", tags=["course"])
async def add_course(
    course: CourseCreateRequest,
    current_user: Annotated[User, Depends(check_and_get_current_teacher)],
    db: AsyncSession = Depends(get_db),
):
    repo = CourseRepository(db)

    result = await repo.create_course(
        course_name=course.course_name,
        teacher_id=current_user.id,
        major_id=course.major_id,
        grade=course.grade,
        course_type=course.course_type,
        course_date=course.course_date,
        credit=course.credit,
        is_public=course.is_public,
    )
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create course")
    return {"msg": "Course created successfully", "course_no": result.course_no}


@router.post("/info", tags=["course"])
async def get_course_info(
    course_no: str,
    current_user: Annotated[User, Depends(check_and_get_current_teacher)],
    db: AsyncSession = Depends(get_db),
):
    repo = CourseRepository(db)
    course = await repo.get_by_course_no(course_no)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/edit", tags=["course"])
async def edit_course(
    course: CourseUpdateRequest,
    current_user: Annotated[User, Depends(check_and_get_current_teacher)],
    db: AsyncSession = Depends(get_db),
):
    repo = CourseRepository(db)
    result = await repo.edit_course(
        course_no=course.course_no,
        course_name=course.course_name,
        teacher_id=current_user.id,
        major_id=course.major_id,
        grade=course.grade,
        course_type=course.course_type,
        course_date=course.course_date,
        credit=course.credit,
        is_public=course.is_public,
    )

    if not result:
        raise HTTPException(status_code=400, detail="Failed to update course")

    return {"msg": "Course updated successfully", "course_no": course.course_no}


@router.delete("/delete", tags=["course"])
async def delete_course(
    course_no: str,
    current_user: Annotated[User, Depends(check_and_get_current_teacher)],
    db: AsyncSession = Depends(get_db),
):
    repo = CourseRepository(db)
    await repo.delete_course(course_no)
    return {"msg": "Course deleted successfully"}


@router.post("/status", tags=["course"])
async def set_course_status(
    course_no: str,
    status: bool,
    current_user: Annotated[User, Depends(check_and_get_current_teacher)],
    db: AsyncSession = Depends(get_db),
):
    repo = CourseRepository(db)
    await repo.set_status(course_no, status)
    return {"msg": "Course status updated successfully"}
