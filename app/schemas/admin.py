from typing import Optional

from models.user import UserRole
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    role: UserRole = Field(..., description="角色", pattern="^(student|teacher|admin)$")
    session: int = Field(..., description="学年")
    faculty: int = Field(..., description="学院ID")
    major: Optional[int] = Field(default=None, description="专业ID")
    class_number: Optional[int] = Field(default=None, description="班级号")
    status: Optional[bool] = Field(default=True, description="用户状态")


class RegisterRequestWithUsername(RegisterRequest):
    name: str = Field(..., description="用户名")


class RegisterResponse(BaseModel):
    name: str = Field(..., description="用户名")
    username: str = Field(..., description="账号ID")
    password: Optional[str] = Field(default=None, description="密码")
