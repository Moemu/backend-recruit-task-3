from datetime import datetime

import sqlalchemy
from core.sql import Base
from sqlalchemy import BigInteger, Boolean, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column


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
