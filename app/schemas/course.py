import enum
from typing import Optional

from pydantic import BaseModel
from typing_extensions import TypedDict


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
    major: int
    session: int
    course_type: CourseType
    course_date: CourseDate
    credit: float
    is_public: bool


class CourseUpdateRequest(BaseModel):
    course_no: str
    course_name: Optional[str] = None
    major: Optional[int] = None
    session: Optional[int] = None
    course_type: Optional[CourseType] = None
    course_date: Optional[CourseDate] = None
    credit: Optional[float] = None
    is_public: Optional[bool] = None
