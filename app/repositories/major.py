from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.major import Major


class MajorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_major_no(self, major_no: str) -> Optional[Major]:
        """
        通过专业编号获得专业对象
        """
        result = await self.session.execute(
            select(Major).where(Major.major_no == major_no)
        )
        return result.scalar_one_or_none()

    async def create_major(
        self,
        major_name: str,
        dept_no: str,
    ) -> Optional[Major]:
        """
        创建一个专业

        :param major_name: 专业名称
        :param dept_no: 院系编号

        :return: 专业对象。失败则返回 None
        """
        majors = await self.session.execute(select(func.count(Major.id)))
        total_majors = (majors.scalar() or 0) + 1
        major_no = f"MA{total_majors:03d}"

        major = Major(major_no=major_no, major_name=major_name, dept_no=dept_no)

        try:
            self.session.add(major)
            await self.session.commit()
        except IntegrityError:
            return None

        return major

    async def edit_major(
        self,
        major_no: str,
        major_name: Optional[str],
        dept_no: Optional[str],
    ) -> Optional[Major]:
        """
        修改一个专业

        :param major_no: 专业编号
        :param major_name: 专业名称
        :param dept_no: 院系编号

        :return: 返回修改后的 Major 对象，若 Major/Department 不存在返回 None
        """
        if not (major := await self.get_by_major_no(major_no)):
            return None

        major.major_name = major_name or major.major_name
        major.dept_no = dept_no or major.dept_no

        try:
            await self.session.commit()
        except IntegrityError:
            return None

        return major

    async def delete_major(self, major_no: str) -> bool:
        """
        删除一个专业

        :param major_no: 专业编号

        :return: 是否成功
        """
        if not (major := await self.get_by_major_no(major_no)):
            return False

        await self.session.delete(major)
        await self.session.commit()

        return True
