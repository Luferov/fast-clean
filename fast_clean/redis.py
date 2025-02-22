"""
Модуль, содержащий функционал, связанный с Redis.
"""

from pydantic import RedisDsn

from redis import asyncio as aioredis


class RedisManager:
    """
    Менеджер для управления клиентом Redis.
    """

    redis: aioredis.Redis | None = None

    @classmethod
    def init(cls, redis_dsn: RedisDsn) -> None:
        """
        Инициализируем клиент Redis.
        """
        if cls.redis is None:
            cls.redis = aioredis.from_url(url=str(redis_dsn), decode_responses=True)
