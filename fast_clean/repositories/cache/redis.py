"""
Module containing the Redis cache repository.
"""

from typing import Self

from fastapi_cache.backends.redis import RedisBackend
from overrides import override
from redis.asyncio.client import Redis


class RedisCacheRepository(RedisBackend):
    """
    Redis cache repository.
    """

    def __init__(self, redis: Redis):
        super().__init__(redis)
        self.redis: Redis

    @override(check_signature=False)
    async def set(self: Self, key: str, value: str, expire: int | None = None, nx: bool = False) -> None:
        """
        Set a value.
        """
        await self.redis.set(key, value, ex=expire, nx=nx)

    async def incr(self: Self, key: str, amount: int = 1) -> int:
        """
        Increment a value.
        """
        return await self.redis.incr(key, amount)

    async def decr(self: Self, key: str, amount: int = 1) -> int:
        """
        Decrement a value.
        """
        return await self.redis.decr(key, amount)

    async def clear(self, namespace: str | None = None, key: str | None = None) -> int:
        """
        Delete a value.

        Parent method does not work correctly and does not count deleted records.
        https://github.com/long2ice/fastapi-cache/issues/241
        """
        if namespace:
            cursor = 0
            removed = 0
            while True:
                cursor, keys = await self.redis.scan(cursor, match=f'{namespace}:*', count=500)
                removed += await self.redis.delete(*keys)
                if cursor == 0:
                    return removed
        elif key:
            return await self.redis.delete(key)
        return 0
