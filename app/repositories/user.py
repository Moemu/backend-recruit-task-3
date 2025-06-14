from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.course import Course, CourseType
from app.models.selection import Selection
from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, username: str) -> Optional[User]:
        """
        通过用户名获得用户对象
        """
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_addition_order(self, prefix: str) -> int:
        """
        获取当前的添加顺序

        :param prefix: 账号前缀
        """
        user = await self.session.execute(
            select(func.count(User.id)).where(User.username.startswith(prefix))
        )
        total_users = user.scalar() or 0
        return total_users + 1

    async def create_user(
        self,
        name: str,
        password: str,
        role: UserRole,
        session: int,
        dept_no: Optional[str] = None,
        major_no: Optional[str] = None,
        class_number: Optional[int] = 0,
        status: bool = True,
    ) -> Optional[User]:
        """
        创建一个用户

        :param name: 姓名
        :param password: 用户哈希密钥
        :param role: 用户角色(student/teacher/admin)
        :param session: 届号
        :param dept_no: 院系ID
        :param major_no: 专业ID
        :param class_number: 班级ID
        :param status: 用户状态(正常/禁用)

        :return: 用户对象。失败则返回 None
        """
        if role == UserRole.student:
            dept = (dept_no and int(dept_no.removeprefix("DP"))) or 0
            major = (major_no and int(major_no.removeprefix("MA"))) or 0
            prefix = f"{session:02d}{dept:03d}{major:02d}{class_number:02d}"
            addition_order = await self.get_addition_order(prefix)
            account_number = f"{prefix}{addition_order:02d}"
        else:
            dept = (dept_no and int(dept_no.removeprefix("DP"))) or 0
            prefix = f"{session:02d}{(dept or 0):03d}"
            addition_order = await self.get_addition_order(prefix)
            account_number = f"{prefix}{addition_order:04d}"

        user = User(
            username=account_number,
            password=password,
            name=name,
            role=role,
            session=session,
            dept_no=dept_no,
            major_no=major_no,
            class_number=class_number,
            status=status,
        )

        try:
            self.session.add(user)
            await self.session.commit()
        except IntegrityError:
            return None

        return user

    async def edit_info(
        self,
        user: User,
        name: Optional[str] = None,
        status: Optional[bool] = None,
        role: Optional[UserRole] = None,
        session: Optional[int] = None,
        major_no: Optional[str] = None,
        dept_no: Optional[str] = None,
        class_number: Optional[int] = None,
    ) -> bool:
        """
        编辑用户信息

        :param user: 用户对象
        :param name: 姓名
        :param role: 用户角色(student/teacher/admin)
        :param status: 用户状态(正常/禁用)
        :param session: 届号
        :param dept_no: 院系ID
        :param major_no: 专业ID
        :param class_number: 班级ID
        """
        user.name = name or user.name
        user.role = role or user.role
        user.status = status or user.status
        user.session = session or user.session
        user.dept_no = dept_no or user.dept_no
        user.major_no = major_no or user.major_no
        user.class_number = class_number or user.class_number

        try:
            await self.session.commit()
        except IntegrityError:
            return False

        return True

    async def change_password(self, user: User, new_password: str):
        """
        修改用户密码

        :param user: 用户对象
        :param new_password: 新密码
        """
        user.password = new_password
        await self.session.commit()

    def _term_filter(self, course_date_column, term: str):
        """
        term json 对象过滤器
        """
        bind = self.session.get_bind()
        if bind.dialect.name == "mysql":
            return course_date_column.op("->>")("$.term") == term
        elif bind.dialect.name == "sqlite":
            return func.json_extract(course_date_column, "$.term") == term
        else:  # pragma: no cover
            return course_date_column["term"] == term

    async def get_schedule(self, user: User, term: str) -> list[Course]:
        """
        获取用户的课程表

        :param user: 用户对象
        :param term: 学期
        """
        major_no = user.major_no
        session = user.session

        # 获取必修课
        core_courses_stmt = select(Course).where(
            Course.major_no == major_no,
            Course.session == session,
            self._term_filter(Course.course_date, term),
            Course.status == 4,
            Course.is_public.is_(True),
            Course.course_type == CourseType.CORE,
        )

        # 获取选修课
        elective_selections_result = await self.session.execute(
            select(Selection.course_id).where(
                Selection.student_id == user.id,
                Selection.status.is_(True),
            )
        )
        elective_course_ids = elective_selections_result.scalars().all()

        elective_courses_stmt = None
        if elective_course_ids:
            elective_courses_stmt = select(Course).where(
                Course.id.in_(elective_course_ids),
                self._term_filter(Course.course_date, term),
            )

        # 组合查询
        if elective_courses_stmt is not None:
            combined_stmt = core_courses_stmt.union(elective_courses_stmt)
        else:
            combined_stmt = core_courses_stmt

        # 将 union 查询包装在 CTE 中，然后从 CTE 中选择 Course 实体
        course_schedule_cte = combined_stmt.cte("course_schedule_cte")
        course_alias = aliased(Course, alias=course_schedule_cte)
        final_query = select(course_alias)

        result = await self.session.execute(final_query)
        courses = result.scalars().all()

        return courses  # type:ignore

    async def delete_user(self, user: User):
        """
        删除用户

        :param user: 用户对象
        """
        await self.session.delete(user)
        await self.session.commit()
