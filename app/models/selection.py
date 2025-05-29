from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.sql import Base

from .course import Course
from .user import User

__table_args__ = (
    UniqueConstraint("student_id", "course_id", name="uq_student_course"),
)


class Selection(Base):
    __tablename__ = "selection"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True, comment="选课 ID"
    )
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, index=True, comment="选课学生ID"
    )
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("course.id"),
        nullable=False,
        index=True,
        comment="目标课程ID",
    )

    selection_time: Mapped[int] = mapped_column(
        DateTime, server_default=func.now(), comment="选课时间"
    )
    status: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="选课状态: 选中/退选"
    )

    student: Mapped[User] = relationship("User", back_populates="course_selections")
    course: Mapped[Course] = relationship("Course", back_populates="student_selections")
