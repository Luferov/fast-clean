"""
Package containing the cache repository.

Two implementations are provided:
- InMemory
- Redis
"""

from typing import ClassVar, Protocol, Self, cast

from fastapi_cache import FastAPICache
from redis import asyncio as aioredis

from fast_clean.settings import CoreCacheSettingsSchema

from .in_memory import InMemoryCacheRepository as InMemoryCacheRepository
from .redis import RedisCacheRepository as RedisCacheRepository


class CacheRepositoryProtocol(Protocol):
    """
    Cache repository protocol.
    """

    async def get(self: Self, key: str) -> str | None:
        """
        Get a value.
        """
        ...

    async def set(self: Self, key: str, value: str, expire: int | None = None, nx: bool = False) -> None:
        """
        Set a value.
        """
        ...

    async def get_with_ttl(self: Self, key: str) -> tuple[int, str | None]:
        """
        Get a value with a TTL.
        """
        ...

    async def incr(self: Self, key: str, amount: int = 1) -> int:
        """
        Increment values.
        """
        ...

    async def decr(self: Self, key: str, amount: int = 1) -> int:
        """
        Decrement values.
        """
        ...

    async def clear(self: Self, namespace: str | None = None, key: str | None = None) -> int:
        """
        Delete a value.
        """
        ...


class CacheManager:
    """
    Manager for working with the cache repository.
    """

    cache_repository: ClassVar[CacheRepositoryProtocol | None] = None

    @classmethod
    def init(cls, cache_settings: CoreCacheSettingsSchema, redis: aioredis.Redis | None) -> None:
        """
        Initialize the cache.
        """
        if cls.cache_repository is None:
            cache_backend: InMemoryCacheRepository | RedisCacheRepository
            match cache_settings.provider:
                case 'in_memory':
                    cache_backend = InMemoryCacheRepository()
                case 'redis':
                    assert redis is not None
                    cache_backend = RedisCacheRepository(redis)
            FastAPICache.init(cache_backend, prefix=cache_settings.prefix)
            cls.cache_repository = cast(CacheRepositoryProtocol, cache_backend)
