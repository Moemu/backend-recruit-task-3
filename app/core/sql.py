from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import config


class Base(DeclarativeBase):
    pass


_engine = create_async_engine(config.db_url, echo=True, pool_pre_ping=True)
async_session = async_sessionmaker(_engine, expire_on_commit=False)


async def load_db():
    """
    初始化表
    """
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    关闭数据库连接
    """
    await _engine.dispose()
