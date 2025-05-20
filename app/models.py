import enum
from datetime import datetime

import sqlalchemy
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

META = sqlalchemy.MetaData()


class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"


class Base(DeclarativeBase):
    pass


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

    major_id: Mapped[int] = mapped_column(BigInteger, nullable=True, comment="专业ID")
    grade: Mapped[int] = mapped_column(Integer, nullable=True, comment="年级")


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键ID"
    )
    course_no: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, comment="课程编号"
    )
    course_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="课程名称"
    )
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="教师ID"
    )
    major_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="专业ID")
    grade: Mapped[int] = mapped_column(Integer, nullable=False, comment="年级")
    course_type: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="课程类型(0-必修, 1-选修)"
    )
    credit: Mapped[float] = mapped_column(Numeric, nullable=False, comment="学分")
    is_public: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=0, comment="是否公开(0-否,1-是)"
    )
    status: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=0, comment="状态(0-正常,1-禁用)"
    )
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


class Department(Base):
    __tablename__ = "department"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键ID"
    )
    dept_no: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False, comment="院系编号"
    )
    dept_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="院系名称"
    )
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


class Major(Base):
    __tablename__ = "major"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键ID"
    )
    major_no: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False, comment="专业编号"
    )
    major_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="专业名称"
    )
    dept_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="院系ID")
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
