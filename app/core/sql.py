from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import config
from app.core.logger import logger


class Base(DeclarativeBase):
    pass


_engine = create_async_engine(config.db_url, echo=False, pool_pre_ping=True)
async_session = async_sessionmaker(_engine, expire_on_commit=False)
async_session_maker = async_sessionmaker(
    bind=_engine, class_=AsyncSession, expire_on_commit=False
)


async def load_db():
    """
    初始化表
    """
    logger.info("初始化数据库表...")
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    关闭数据库连接
    """
    await _engine.dispose()
