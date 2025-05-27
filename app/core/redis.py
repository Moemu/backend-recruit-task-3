import redis.asyncio as redis

from .config import config

redis_client = redis.Redis(
    host=config.redis_host, port=config.redis_port, db=0, decode_responses=True
)
