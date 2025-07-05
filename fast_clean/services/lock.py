"""
Модуль, содержащий сервис распределенной блокировки.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import AsyncContextManager, Protocol

from fast_clean.exceptions import LockError
from redis import asyncio as aioredis
from redis.exceptions import LockError as AIORedisLockError


class LockServiceProtocol(Protocol):
    """
    Протокол сервиса распределенной блокировки.
    """

    def lock(
        self,
        name: str,
        *,
        timeout: float | None = None,
        sleep: float = 0.1,
        blocking_timeout: float | None = None,
    ) -> AsyncContextManager[None]:
        """
        Осуществляем распределенную блокировку.
        """
        ...


class RedisLockService:
    """
    Сервис распределенной блокировки с помощью Redis.
    """

    def __init__(self, redis: aioredis.Redis) -> None:
        self.redis = redis

    @asynccontextmanager
    async def lock(
        self,
        name: str,
        *,
        timeout: float | None = None,
        sleep: float = 0.1,
        blocking_timeout: float | None = None,
    ) -> AsyncIterator[None]:
        """
        Осуществляем распределенную блокировку.
        """
        try:
            async with self.redis.lock(name, timeout=timeout, sleep=sleep, blocking_timeout=blocking_timeout):
                yield
        except AIORedisLockError as lock_error:
            raise LockError() from lock_error
