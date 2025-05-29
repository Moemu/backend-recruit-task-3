import enum
from datetime import datetime

import sqlalchemy
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import TypedDict

from app.core.sql import Base


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


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID"
    )
    course_no: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, comment="课程编号"
    )
    course_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="课程名称"
    )

    teacher: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), comment="教师ID"
    )
    major_no: Mapped[str] = mapped_column(
        String(10), ForeignKey("major.major_no"), comment="专业编号"
    )
    session: Mapped[int] = mapped_column(Integer, nullable=False, comment="年级")
    course_type: Mapped[CourseType] = mapped_column(
        Enum(CourseType), nullable=False, comment="课程类型(0-必修, 1-选修)"
    )
    credit: Mapped[float] = mapped_column(Numeric, nullable=False, comment="学分")
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否公开")
    status: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="课程状态(1-已提交/2-审核通过/3-审核不通过/4-公开/0-隐藏)",
    )
    status_comment: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="状态说明"
    )

    max_students: Mapped[int] = mapped_column(
        Integer, nullable=True, default=50, comment="选修课·最大选课人数"
    )
    current_students: Mapped[int] = mapped_column(
        Integer, default=0, comment="选修课·当前已选人数"
    )

    course_date: Mapped[CourseDate] = mapped_column(
        JSON, nullable=False, comment="课程时间"
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

    student_selections = relationship(
        "Selection", back_populates="course", cascade="all, delete-orphan"
    )
