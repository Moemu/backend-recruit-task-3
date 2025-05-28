from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department


class DepartmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_dept_no(self, dept_no: str) -> Optional[Department]:
        """
        通过院系编号获得院系对象
        """
        result = await self.session.execute(
            select(Department).where(Department.dept_no == dept_no)
        )
        return result.scalar_one_or_none()

    async def create_department(
        self,
        dept_name: str,
    ) -> Department:
        """
        创建一个院系

        :param dept_name: 院系名称
        """
        departments = await self.session.execute(select(func.count(Department.id)))
        total_departments = (departments.scalar() or 0) + 1
        dept_no = f"DP{total_departments:03d}"

        department = Department(dept_no=dept_no, dept_name=dept_name)

        self.session.add(department)
        await self.session.commit()
        return department

    async def edit_department(
        self,
        dept_no: str,
        dept_name: str,
    ) -> Optional[Department]:
        """
        修改一个院系

        :param dept_no: 院系编号
        :param department_name: 院系名称

        :return: 返回修改后的 Department 对象，若 Department 不存在返回 None
        """
        if not (department := await self.get_by_dept_no(dept_no)):
            return None

        department.dept_name = dept_name or department.dept_name

        await self.session.commit()
        return department

    async def delete_department(self, dept_no: str) -> bool:
        """
        删除一个院系

        :param dept_no: 院系编号

        :return: 是否成功
        """
        if not (department := await self.get_by_dept_no(dept_no)):
            return False

        await self.session.delete(department)
        await self.session.commit()

        return True
