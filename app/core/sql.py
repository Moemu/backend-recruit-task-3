import asyncio

from core.config import config
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import Base

_engine = create_async_engine(config.db_url, echo=True)
async_session = async_sessionmaker(_engine, expire_on_commit=False)


async def _init_models():
    """
    初始化表
    """
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(_init_models())
