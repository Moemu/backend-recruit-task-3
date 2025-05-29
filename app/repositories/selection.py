# app/repositories/selection.py
from typing import List, Optional

from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import Course, CourseType
from app.models.selection import Selection


class SelectionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_selection_by_id(self, selection_id: int) -> Optional[Selection]:
        """
        通过 selection id 获取选课对象
        """
        result = await self.session.execute(
            select(Selection)
            .where(Selection.id == selection_id)
            .order_by(Selection.id)
            .options(
                selectinload(Selection.student), selectinload(Selection.course)
            )  # 预加载学生对象和课程对象
        )
        return result.scalars().first()

    async def get_selection_by_student_and_course(
        self, student_id: int, course_id: int
    ) -> Optional[Selection]:
        """
        通过学生 ID 和课程 ID 获取选课对象
        常用于查询是否已经选课
        """
        result = await self.session.execute(
            select(Selection).where(
                Selection.student_id == student_id, Selection.course_id == course_id
            )
        )
        return result.scalars().first()

    async def get_selections_by_student_id(
        self, student_id: int, skip: int = 0, limit: int = 100
    ) -> List[Selection]:
        """
        通过学生 ID 获取选课对象

        :param student_id: 学生ID
        :param skip: 跳过记录数值（分页）
        :param limit: 最大返回记录（分页）
        """
        result = await self.session.execute(
            select(Selection)
            .where(Selection.student_id == student_id)
            .options(selectinload(Selection.course))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()  # type:ignore

    async def get_available_courses(
        self, student_id: int, term: str, skip: int = 0, limit: int = 100
    ) -> List[Course]:
        """
        获取学生可选的课程列表

        :param student_id: 学生 ID
        :param term: 学期
        :param skip: 跳过记录数值（分页）
        :param limit: 最大返回记录（分页）
        """
        result = await self.session.execute(
            select(Course)
            .where(
                Course.is_public.is_(True),
                Course.status == 4,
                Course.course_date["term"] == term,
                Course.course_type == CourseType.ELECTIVE,
                Course.id.not_in(
                    select(Selection.course_id).where(
                        Selection.student_id == student_id
                    )
                ),
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()  # type:ignore

    async def get_selections_by_course_id(
        self, course_id: int, skip: int = 0, limit: int = 100
    ) -> List[Selection]:
        """
        通过课程 ID 获取选课对象

        :param course_id: 课程 ID
        :param skip: 跳过记录数值（分页）
        :param limit: 最大返回记录（分页）
        """
        result = await self.session.execute(
            select(Selection)
            .where(Selection.course_id == course_id)
            .options(selectinload(Selection.student))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()  # type:ignore

    async def create_selection(self, student_id: int, course_no: str) -> Selection:
        """
        创建选课对象（选课）

        :param student_id: 用户 ID
        :param course_no: 目标课程编号(只能选选修课)

        :return: 选课对象

        :raise HTTPException: 当找不到该课程、课程已满、选中了必修课、重复选课时抛出此异常
        """
        courses = await self.session.execute(
            select(Course).where(Course.course_no == course_no)
        )
        course = courses.scalars().first()
        if not course:
            raise HTTPException(
                status_code=404, detail=f"Course with id {course_no} not found"
            )

        # 检查最大选课限制
        if (
            course.max_students is not None
            and course.current_students >= course.max_students
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Course {course_no} is full. Maximum capacity: {course.max_students}",
            )

        # 检查为什么必修课也得选
        if course.course_type == CourseType.CORE:
            raise HTTPException(
                status_code=400,
                detail="Compulsory courses can be included in your schedule without selecting them, ass hole",
            )

        # 检查是否重复选课
        existing_selection = await self.get_selection_by_student_and_course(
            student_id=student_id, course_id=course.id
        )

        if existing_selection and existing_selection.status:
            raise HTTPException(
                status_code=400,
                detail=f"Student {student_id} has already an active selection for course {course_no}",
            )

        # 更新课程当前选课人数
        course.current_students += 1
        self.session.add(course)

        db_selection = Selection(
            student_id=student_id,
            course_id=course.id,
            status=True,
        )
        self.session.add(db_selection)
        await self.session.commit()
        await self.session.refresh(db_selection)
        return db_selection

    async def update_selection_status(
        self, selection_id: int, new_status: bool
    ) -> Optional[Selection]:
        """
        更新选课状态

        :param selection_id: 选课ID
        :param new_status: 选课状态

        :return: 选课对象，如果不存在则返回 None

        :raise HTTPException: 如果不是发起退课就抛出此异常
        """
        db_selection = await self.get_selection_by_id(selection_id)
        if not db_selection:
            raise HTTPException(
                status_code=404, detail=f"Selection with id {selection_id} not found"
            )

        # 选中 -> 退课
        if (not new_status) and new_status != db_selection.status:
            course = db_selection.course
            course.current_students -= 1
            self.session.add(course)
        elif new_status == db_selection.status:
            raise HTTPException(
                status_code=400,
                detail="The modified status cannot be the same as the original status!",
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="You can't select the course by using this selection after quitting this."
                "You need to recreate the course selection",
            )

        db_selection.status = new_status
        self.session.add(db_selection)
        await self.session.commit()
        await self.session.refresh(db_selection)
        return db_selection
