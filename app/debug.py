from app.core.logger import logger
from app.deps.sql import get_db
from app.models.user import UserRole
from app.repositories.user import UserRepository
from app.services.auth_service import get_password_hash

ADMIN_NAME = "admin"
ADMIN_PWD = "123456"


async def create_a_debug_admin():
    """
    创建一个测试管理员账号
    """
    async for db in get_db():
        repo = UserRepository(db)

    user = await repo.create_user(
        name=ADMIN_NAME,
        password=get_password_hash(ADMIN_PWD),
        role=UserRole.admin,
        session=25,
        dept_no=1,
    )

    return user


if __name__ == "__main__":
    import asyncio

    user = asyncio.run(create_a_debug_admin())
    logger.info("成功创建了一个测试账号✨")
    logger.info(f"账号: {user.username}, 密码: {ADMIN_PWD}")
