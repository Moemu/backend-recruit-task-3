from typing import Literal, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserRole


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
    ):
        """
        创建一个用户

        :param username: 用户名
        :param password: base64 用户密钥
        :param role: 用户角色(student/teacher/admin)
        :param status: 用户状态(0-正常/1-禁用)
        """
        user = User(username=username, password=password, role=role, status=status)
        self.session.add(user)
        await self.session.commit()
        return user
