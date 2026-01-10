"""
Module containing Redis-related functionality.
"""

from pydantic import RedisDsn
from redis import asyncio as aioredis


class RedisManager:
    """
    Manager for controlling the Redis client.
    """

    redis: aioredis.Redis | None = None

    @classmethod
    def init(cls, redis_dsn: RedisDsn) -> None:
        """
        Initialize the Redis client.
        """
        if cls.redis is None:
            cls.redis = aioredis.from_url(url=str(redis_dsn), decode_responses=True)
