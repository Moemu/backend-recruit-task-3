import enum
from datetime import datetime

import sqlalchemy
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.sql import Base


class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID"
    )
    username: Mapped[str] = mapped_column(
        String(12), unique=True, nullable=False, comment="用户ID"
    )
    password: Mapped[str] = mapped_column(String(100), nullable=False, comment="密码")
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False, comment="角色(ADMIN/TEACHER/STUDENT)"
    )
    status: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="状态(正常/禁用)"
    )

    name: Mapped[str] = mapped_column(String(12), nullable=False, comment="姓名")
    session: Mapped[int] = mapped_column(Integer, nullable=False, comment="届号")
    dept_no: Mapped[int] = mapped_column(
        Integer, ForeignKey("department.dept_no"), nullable=False, comment="院系ID"
    )
    major_no: Mapped[int] = mapped_column(
        Integer, ForeignKey("major.major_no"), nullable=True, comment="专业ID"
    )
    class_number: Mapped[int] = mapped_column(Integer, nullable=True, comment="班级ID")

    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        comment="创建时间",
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
        comment="更新时间",
    )
