from typing import Literal, Optional

from models.user import User, UserRole
from sqlalchemy import select
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

    async def create_user(
        self, username: str, password: str, role: UserRole, status: Literal[0, 1] = 0
    ) -> Optional[User]:
        """
        创建一个用户

        :param username: 用户名
        :param password: 用户哈希密钥
        :param role: 用户角色(student/teacher/admin)
        :param status: 用户状态(0-正常/1-禁用)
        """
        if await self.get_by_name(username):
            return None
        user = User(username=username, password=password, role=role, status=status)
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
