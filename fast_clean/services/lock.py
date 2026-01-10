"""
Module containing the distributed lock service.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import AsyncContextManager, Protocol

from redis import asyncio as aioredis
from redis.exceptions import LockError as AIORedisLockError

from fast_clean.exceptions import LockError


class LockServiceProtocol(Protocol):
    """
    Distributed lock service protocol.
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
        Perform distributed locking.
        """
        ...


class RedisLockService:
    """
    Distributed lock service using Redis.
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
        Perform distributed locking.
        """
        try:
            async with self.redis.lock(name, timeout=timeout, sleep=sleep, blocking_timeout=blocking_timeout):
                yield
        except AIORedisLockError as lock_error:
            raise LockError() from lock_error
