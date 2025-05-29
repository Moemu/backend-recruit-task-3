from typing import Optional

import fastapi
from fastapi.exceptions import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models.course import Course, CourseDate, CourseType


class CourseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_course_no(self, course_no: str) -> Optional[Course]:
        """
        通过课程编号获得课程对象
        """
        result = await self.session.execute(
            select(Course).where(Course.course_no == course_no)
        )
        return result.scalar_one_or_none()

    async def create_course(
        self,
        course_name: str,
        teacher: int,
        major_no: str,
        session: int,
        course_type: CourseType,
        credit: float,
        course_date: CourseDate,
        is_public: bool = True,
        status: int = 0,
        max_students: Optional[int] = 50,
    ):
        """
        创建一个课程

        :param course_name: 课程名称
        :param teacher_id: 任教教师ID
        :param major_no: 专业ID
        :param session: 年级
        :param course_type: 课程类型(0-必修, 1-选修)
        :param course_date: 课程时间
        :param credit: 学分
        :param is_public: 是否公开
        :param status: 课程状态
        :param max_students: 选修课最大选课人数

        :return: 课程对象。失败则返回 None
        """
        courses = await self.session.execute(select(func.count(Course.id)))
        total_courses = (courses.scalar() or 0) + 1
        course_no = f"CS{total_courses:03d}"
        course = Course(
            course_no=course_no,
            course_name=course_name,
            teacher=teacher,
            major_no=major_no,
            session=session,
            course_type=course_type.value,
            credit=credit,
            course_date=course_date,
            is_public=is_public,
            status=status,
            max_students=max_students,
        )
        self.session.add(course)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail="Course already exists",
            )
        return course

    async def edit_course(
        self,
        course_no: str,
        course_name: Optional[str] = None,
        teacher: Optional[int] = None,
        major_no: Optional[str] = None,
        session: Optional[int] = None,
        course_type: Optional[CourseType] = None,
        course_date: Optional[CourseDate] = None,
        credit: Optional[float] = None,
        is_public: Optional[bool] = None,
        status: Optional[bool] = None,
        max_students: Optional[int] = None,
    ) -> Optional[Course]:
        """
        修改一个课程

        :param couse_no: 课程编号
        :param course_name: 课程名称
        :param teacher: 任教教师ID
        :param major_no: 专业ID
        :param grade: 年级
        :param course_type: 课程类型(0-必修, 1-选修)
        :param course_date: 课程时间
        :param credit: 学分
        :param is_public: 是否公开
        :param status: 课程状态
        :param max_students: 选修课最大选课人数

        :return: 修改后的课程对象。失败则返回 None
        """
        if not (course := await self.get_by_course_no(course_no)):
            return None

        course.course_name = course_name or course.course_name
        course.teacher = teacher or course.teacher
        course.major_no = major_no or course.major_no
        course.session = session or course.session
        course.course_type = course_type or course.course_type
        course.course_date = course_date or course.course_date
        course.credit = credit or course.credit
        course.is_public = is_public or course.is_public
        course.status = status or course.status
        course.max_students = max_students or course.max_students

        try:
            await self.session.commit()
        except IntegrityError:
            return None

        return course

    async def delete_course(self, course_no: str) -> bool:
        """
        删除一个课程

        :param course_no: 课程编号

        :return: 是否成功
        """
        if not (course := await self.get_by_course_no(course_no)):
            return False

        await self.session.delete(course)
        await self.session.commit()

        return True

    async def submit_course_review(self, course_no: str):
        """
        提交课程审核

        :param course_no: 课程编号

        :return: 是否成功

        :raises HTTPException: 如果课程不存在或状态不符合要求
        """
        if not (course := await self.get_by_course_no(course_no)):
            logger.warning(f"课程: {course_no} 不存在，返回 404")
            raise HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        if course.status != 0:
            logger.warning(f"课程: {course_no} 状态不符合要求，返回 400")
            raise HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail="Course is not in a valid state for submission",
            )

        course.status = 1
        await self.session.commit()

        return True

    async def set_course_status(
        self, course_no: str, status: int, comment: Optional[str] = None
    ) -> Course:
        """
        设置课程状态（审核课程）

        :param course_no: 课程编号
        :param status: 审核状态(1-待审核, 2-通过, 3-不通过, 4-公开, 0-隐藏)
        :param comment: 状态说明（可选）

        :raises HTTPException: 如果状态无效或课程不存在
        """
        if not (course := await self.get_by_course_no(course_no)):
            logger.warning(f"课程: {course_no} 不存在，返回 404")
            raise HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        if status not in [1, 2, 3, 4, 0]:
            logger.warning(f"课程: {course_no} 状态不符合要求，返回 400")
            raise HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail="Invalid course status",
            )

        course.status = status
        if comment:
            course.status_comment = comment

        await self.session.commit()
        return course

    async def get_pending_courses(self) -> list[Course]:
        """
        获取所有待审核的课程

        :return: 待审核课程列表
        """
        result = await self.session.execute(select(Course).where(Course.status == 1))
        return result.scalars().all()  # type: ignore
