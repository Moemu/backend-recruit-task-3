import enum
from datetime import datetime

import sqlalchemy
from core.sql import Base
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column


class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键ID"
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="用户名"
    )
    password: Mapped[str] = mapped_column(String(100), nullable=False, comment="密码")
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False, comment="角色(ADMIN/TEACHER/STUDENT)"
    )
    status: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="状态(0-正常,1-禁用)"
    )

    major_id: Mapped[int] = mapped_column(BigInteger, nullable=True, comment="专业ID")
    grade: Mapped[int] = mapped_column(Integer, nullable=True, comment="年级")

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
