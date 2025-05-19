from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal
from enum import Enum

class UserRole(str, Enum):
    admin = "ADMIN"
    teacher = "TEACHER"
    student = "STUDENT"

class BaseUser(BaseModel):
    """
    用户基类
    """
    id: int
    username: str
    password: str
    role: Literal["ADMIN", "TEACHER", "STUDENT"]
    status: int = 0
    create_time: datetime
    update_time: datetime

class Teacher(BaseUser):
    """
    教师实体类
    """
    teacher_no: str
    department_id: int
    name: str
    phone: Optional[str]
    email: Optional[str]

class Course(BaseModel):
    """
    课程实体类
    """
    id: int
    course_no: str
    course_name: str
    teacher_id: int
    major_id: int
    grade: int
    course_type: int
    credit: float
    is_public: bool
    status: bool
    create_time: datetime
    update_time: datetime

class Department(BaseModel):
    """
    院系实体类
    """
    id: int
    dept_no: str
    dept_name: str
    create_time: datetime
    update_time: datetime

class major(BaseModel):
    """
    专业实体类
    """
    id: int
    major_no: str
    major_name: str
    dept_id: int
    create_time: datetime
    update_time: datetime