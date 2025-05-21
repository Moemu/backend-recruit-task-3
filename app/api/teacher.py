from typing import Annotated

from api._auth import check_and_get_current_teacher
from deps import get_db
from fastapi import APIRouter, Depends, HTTPException
from models.course import CourseType
from models.user import User
from repositories.course import CourseRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/add", tags=["course"])
async def add_course(
    course_name: str,
    major_id: int,
    grade: int,
    course_type: CourseType,
    credit: float,
    is_public: bool,
    current_user: Annotated[User, Depends(check_and_get_current_teacher)],
    db: AsyncSession = Depends(get_db),
):
    repo = CourseRepository(db)
    course = await repo.create_course(
        course_name=course_name,
        teacher_id=current_user.id,
        major_id=major_id,
        grade=grade,
        course_type=course_type,
        credit=credit,
        is_public=is_public,
    )
    if not course:
        raise HTTPException(status_code=400, detail="Failed to create course")
    return {"msg": "Course created successfully", "course_no": course.course_no}


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
    course_no: str,
    course_name: str,
    major_id: int,
    grade: int,
    course_type: CourseType,
    credit: float,
    is_public: bool,
    current_user: Annotated[User, Depends(check_and_get_current_teacher)],
    db: AsyncSession = Depends(get_db),
):
    repo = CourseRepository(db)
    course = await repo.edit_course(
        course_no=course_no,
        course_name=course_name,
        teacher_id=current_user.id,
        major_id=major_id,
        grade=grade,
        course_type=course_type,
        credit=credit,
        is_public=is_public,
    )

    if not course:
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
