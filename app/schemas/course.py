from typing import Optional

from pydantic import BaseModel

from app.models.course import CourseDate, CourseType


class CourseCreateRequest(BaseModel):
    course_name: str
    major_no: str
    session: int
    course_type: CourseType
    course_date: CourseDate
    credit: float
    is_public: bool
    max_students: Optional[int] = 50


class CourseUpdateRequest(BaseModel):
    course_no: str
    course_name: Optional[str] = None
    major_no: Optional[str] = None
    session: Optional[int] = None
    course_type: Optional[CourseType] = None
    course_date: Optional[CourseDate] = None
    credit: Optional[float] = None
    is_public: Optional[bool] = None
    max_students: Optional[int] = None
