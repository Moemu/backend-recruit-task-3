from collections.abc import AsyncGenerator

import redis.asyncio as redis

from app.core.logger import logger

from .config import config


async def get_redis_client() -> AsyncGenerator[redis.Redis, None]:
    logger.info("初始化 Redis 实例...")

    client = redis.Redis(
        host=config.redis_host, port=config.redis_port, decode_responses=True
    )
    try:
        yield client
    finally:
        await client.aclose()
