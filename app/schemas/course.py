import enum
from typing import TypedDict

from pydantic import BaseModel


class CourseType(int, enum.Enum):
    CORE = 0
    ELECTIVE = 1


class CourseDate(TypedDict):
    term: str
    start_week: int
    end_week: int
    is_double_week: bool
    week_day: int
    section: list[int]


class CourseCreateRequest(BaseModel):
    course_name: str
    major_id: int
    grade: int
    course_type: CourseType
    course_date: CourseDate
    credit: float
    is_public: bool


class CourseUpdateRequest(BaseModel):
    course_no: str
    course_name: str
    major_id: int
    grade: int
    course_type: CourseType
    course_date: CourseDate
    credit: float
    is_public: bool
