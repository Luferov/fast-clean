"""
Пакет, содержащий репозиторий кеша.

Представлено две реализации:
- InMemory
- Redis
"""

from typing import ClassVar, Protocol, Self, cast

from fastapi_cache import FastAPICache

from fast_clean.settings import CoreCacheSettingsSchema
from redis import asyncio as aioredis

from .in_memory import InMemoryCacheRepository as InMemoryCacheRepository
from .redis import RedisCacheRepository as RedisCacheRepository


class CacheRepositoryProtocol(Protocol):
    """
    Протокол репозитория кеша.
    """

    async def get(self: Self, key: str) -> str | None:
        """
        Получаем значение.
        """
        ...

    async def set(self: Self, key: str, value: str, expire: int | None = None, nx: bool = False) -> None:
        """
        Устанавливаем значение.
        """
        ...

    async def get_with_ttl(self: Self, key: str) -> tuple[int, str | None]:
        """
        Получаем значение со сроком жизни.
        """
        ...

    async def incr(self: Self, key: str, amount: int = 1) -> int:
        """
        Инкрементируем значения.
        """
        ...

    async def decr(self: Self, key: str, amount: int = 1) -> int:
        """
        Декрементируем значения.
        """
        ...

    async def clear(self: Self, namespace: str | None = None, key: str | None = None) -> int:
        """
        Удаляем значение.
        """
        ...


class CacheManager:
    """
    Менеджер для работы с репозиторием кеша.
    """

    cache_repository: ClassVar[CacheRepositoryProtocol | None] = None

    @classmethod
    def init(cls, cache_settings: CoreCacheSettingsSchema, redis: aioredis.Redis | None) -> None:
        """
        Инициализируем кеш.
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
