from datetime import datetime

import sqlalchemy
from sqlalchemy import JSON, BigInteger, Boolean, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.sql import Base
from app.schemas.course import CourseDate


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
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="教师ID"
    )
    major: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="专业ID")
    session: Mapped[int] = mapped_column(Integer, nullable=False, comment="年级")
    course_type: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="课程类型(0-必修, 1-选修)"
    )
    credit: Mapped[float] = mapped_column(Numeric, nullable=False, comment="学分")
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否公开")
    status: Mapped[int] = mapped_column(
        Integer,
        default=True,
        comment="课程状态(1-已提交/2-审核通过/3-审核不通过/4-公开/0-隐藏)",
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
