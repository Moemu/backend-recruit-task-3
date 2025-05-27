from collections.abc import AsyncGenerator

import redis.asyncio as redis

from .config import config


async def get_redis_client() -> AsyncGenerator[redis.Redis, None]:
    client = redis.Redis(
        host=config.redis_host, port=config.redis_port, decode_responses=True
    )
    try:
        yield client
    finally:
        await client.aclose()
