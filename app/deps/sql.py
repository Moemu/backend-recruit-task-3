from typing import AsyncGenerator

from app.core.sql import async_session


async def get_db() -> AsyncGenerator:
    async with async_session() as session:
        yield session
