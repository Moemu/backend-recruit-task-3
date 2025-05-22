from typing import Optional

import fastapi
from fastapi.exceptions import HTTPException
from models.course import Course, CourseDate, CourseType
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


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
        teacher_id: int,
        major_id: int,
        grade: int,
        course_type: CourseType,
        credit: float,
        course_date: CourseDate,
        is_public: bool = True,
        status: bool = True,
    ):
        """
        创建一个课程

        :param course_name: 课程名称
        :param teacher_id: 任教教师ID
        :param major_id: 专业ID
        :param grade: 年级
        :param course_type: 课程类型(0-必修, 1-选修)
        :param course_date: 课程时间
        :param credit: 学分
        :param is_public: 是否公开
        :param status: 课程状态
        """
        courses = await self.session.execute(select(func.count(Course.id)))
        total_courses = courses.scalar() or 1
        course_no = f"CS{total_courses:03d}"
        course = Course(
            course_no=course_no,
            course_name=course_name,
            teacher_id=teacher_id,
            major_id=major_id,
            grade=grade,
            course_type=course_type.value,
            credit=credit,
            course_date=course_date,
            is_public=is_public,
            status=status,
        )
        self.session.add(course)
        await self.session.commit()
        return course

    async def edit_course(
        self,
        course_no: str,
        course_name: str,
        teacher_id: int,
        major_id: int,
        grade: int,
        course_type: CourseType,
        course_date: CourseDate,
        credit: float,
        is_public: bool = True,
        status: bool = True,
    ):
        """
        修改一个课程

        :param couse_no: 课程编号
        :param course_name: 课程名称
        :param teacher_id: 任教教师ID
        :param major_id: 专业ID
        :param grade: 年级
        :param course_type: 课程类型(0-必修, 1-选修)
        :param course_date: 课程时间
        :param credit: 学分
        :param is_public: 是否公开
        :param status: 课程状态
        """
        if not (course := await self.get_by_course_no(course_no)):
            raise HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail="Incorrect course_no",
            )
        course.course_name = course_name
        course.teacher_id = teacher_id
        course.major_id = major_id
        course.grade = grade
        course.course_type = course_type.value
        course.course_date = course_date
        course.credit = credit
        course.is_public = is_public
        course.status = status
        await self.session.commit()
        return course

    async def delete_course(self, course_no: str) -> bool:
        """
        删除一个课程

        :param course_no: 课程编号
        """
        if not (course := await self.get_by_course_no(course_no)):
            raise HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail="Incorrect course_no",
            )
        await self.session.delete(course)
        await self.session.commit()
        return True

    async def set_status(self, course_no: str, status: bool):
        """
        设置课程状态

        :param course_no: 课程编号
        :param status: 课程状态
        """
        if not (course := await self.get_by_course_no(course_no)):
            raise HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail="Incorrect course_no",
            )
        course.status = status
        await self.session.commit()
