from typing import Optional

from models.user import User, UserRole
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


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

    async def get_addition_order(self, role: UserRole) -> int:
        """
        获取当前的添加顺序
        """
        user = await self.session.execute(
            select(func.count(User.id)).where(User.role == role)
        )
        total_users = user.scalar() or 1
        return total_users

    async def create_user(
        self,
        username: str,
        password: str,
        role: UserRole,
        session: int,
        faculty: int,
        major: Optional[int] = None,
        class_number: Optional[int] = None,
        status: bool = True,
    ) -> Optional[User]:
        """
        创建一个用户

        :param username: 用户名
        :param password: 用户哈希密钥
        :param role: 用户角色(student/teacher/admin)
        :param session: 学年
        :param faculty: 院系ID
        :param major: 专业ID
        :param class_number: 班级ID
        :param status: 用户状态(正常/禁用)
        """
        if await self.get_by_name(username):
            return None
        addition_order = await self.get_addition_order(role)
        if role == UserRole.student:
            account_number = f"{session:02d}{faculty:03d}{major:02d}{class_number:02d}{addition_order:02d}"
        else:
            account_number = f"{session:02d}{faculty:02d}{addition_order:03d}"
        user = User(
            username=username,
            password=password,
            account_number=account_number,
            role=role,
            status=status,
        )
        self.session.add(user)
        await self.session.commit()
        return user

    async def edit_info(
        self,
        user: User,
        username: str,
        status: bool,
        major_id: int,
        grade: int,
    ):
        """
        编辑用户信息

        :param user: 用户对象
        :param username: 用户名
        :param status: 用户状态(0-正常/1-禁用)
        :param major_id: 专业ID
        :param grade: 年级
        """
        user.username = username
        user.status = status
        user.major_id = major_id
        user.grade = grade
        await self.session.commit()

    async def change_password(self, user: User, new_password: str):
        """
        修改用户密码

        :param user: 用户对象
        :param new_password: 新密码
        """
        user.password = new_password
        await self.session.commit()
