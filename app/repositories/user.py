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
