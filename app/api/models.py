from dataclasses import asdict, dataclass
from typing import Optional
from uuid import uuid4

from models.course import CourseDate, CourseType
from pydantic import BaseModel


class Token(BaseModel):
    """
    jwt 密钥实体
    """

    access_token: str
    token_type: str


@dataclass
class Payload:
    """
    jwt Payload
    """

    sub: str
    """用户名"""
    exp: Optional[int] = None
    """过期时间"""
    jti: str = str(uuid4())
    """JWT ID"""

    def to_json(self):
        return asdict(self)


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
