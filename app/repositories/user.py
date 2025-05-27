from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole

from .course import Course


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
        total_users = user.scalar() or 1
        return total_users

    async def create_user(
        self,
        name: str,
        password: str,
        role: UserRole,
        session: int,
        faculty: int,
        major: Optional[int] = None,
        class_number: Optional[int] = None,
        status: bool = True,
    ) -> User:
        """
        创建一个用户

        :param name: 姓名
        :param password: 用户哈希密钥
        :param role: 用户角色(student/teacher/admin)
        :param session: 届号
        :param faculty: 院系ID
        :param major: 专业ID
        :param class_number: 班级ID
        :param status: 用户状态(正常/禁用)

        :return: 用户对象
        """
        if role == UserRole.student:
            prefix = f"{session:02d}{faculty:03d}{major:02d}{class_number:02d}"
            addition_order = await self.get_addition_order(prefix)
            account_number = f"{prefix}{addition_order:02d}"
        else:
            prefix = f"{session:02d}{faculty:03d}"
            addition_order = await self.get_addition_order(prefix)
            account_number = f"{prefix}{addition_order:04d}"

        user = User(
            username=account_number,
            password=password,
            name=name,
            role=role,
            session=session,
            faculty=faculty,
            major=major,
            class_number=class_number,
            status=status,
        )
        self.session.add(user)
        await self.session.commit()
        return user

    async def edit_info(
        self,
        user: User,
        name: Optional[str] = None,
        status: Optional[bool] = None,
        role: Optional[UserRole] = None,
        major: Optional[int] = None,
        session: Optional[int] = None,
        faculty: Optional[int] = None,
        class_number: Optional[int] = None,
    ):
        """
        编辑用户信息

        :param user: 用户对象
        :param name: 姓名
        :param role: 用户角色(student/teacher/admin)
        :param status: 用户状态(正常/禁用)
        :param session: 届号
        :param faculty: 院系ID
        :param major: 专业ID
        :param class_number: 班级ID
        """
        user.name = name or user.name
        user.role = role or user.role
        user.status = status or user.status
        user.session = session or user.session
        user.faculty = faculty or user.faculty
        user.major = major or user.major
        user.class_number = class_number or user.class_number
        await self.session.commit()

    async def change_password(self, user: User, new_password: str):
        """
        修改用户密码

        :param user: 用户对象
        :param new_password: 新密码
        """
        user.password = new_password
        await self.session.commit()

    async def get_schedule(self, user: User, term: str) -> list[Course]:
        """
        获取用户的课程表

        :param user: 用户对象
        :param term: 学期
        """
        major = user.major
        session = user.session
        courses = await self.session.execute(
            select(Course).where(
                Course.major == major,
                Course.session == session,
                Course.course_date["term"] == term,
                Course.status == 4,
                Course.is_public == True,  # noqa: E712
            )
        )
        return courses.scalars().all()  # type: ignore

    async def delete_user(self, user: User):
        """
        删除用户

        :param user: 用户对象
        """
        await self.session.delete(user)
        await self.session.commit()
