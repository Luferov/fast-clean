"""
Модуль, содержащий тесты репозиториев кеша.
"""

import asyncio

import pytest
from fast_clean.repositories.cache import CacheRepositoryProtocol

STR_KEY = 'str_key'
STR_VALUE = 'str_value'
INT_KEY = 'int_key'
INT_VALUE = 1
NAMESPACE = 'namespace'
NAMESPACE_CACHE_DATA = {
    f'{NAMESPACE}:key1': 'namespace_value1',
    f'{NAMESPACE}:key2': 'namespace_value2',
}
CACHE_DATA = {STR_KEY: STR_VALUE, 'int_key': str(INT_VALUE), **NAMESPACE_CACHE_DATA}

NEW_KEY = 'new_key'
NEW_VALUE = 'new_value'
NEW_VALUE_EXTRA = 'new_value_extra'
EXPIRE = 5


@pytest.mark.parametrize(
    'cache_repository',
    [('in_memory', CACHE_DATA), ('redis', CACHE_DATA)],
    indirect=True,
)
class TestCacheRepositories:
    """
    Тесты репозиториев кеша.
    """

    @classmethod
    async def test_get(cls, cache_repository: CacheRepositoryProtocol) -> None:
        """
        Тестируем метод `get`.
        """
        for key, expected_value in CACHE_DATA.items():
            assert await cache_repository.get(key) == expected_value
        assert await cache_repository.get('unknown_key') is None

    @classmethod
    async def test_set(cls, cache_repository: CacheRepositoryProtocol) -> None:
        """
        Тестируем метод `set`.
        """
        assert await cache_repository.get(NEW_KEY) is None
        await cache_repository.set(NEW_KEY, NEW_VALUE)
        assert await cache_repository.get(NEW_KEY) == NEW_VALUE
        await cache_repository.set(NEW_KEY, NEW_VALUE_EXTRA, nx=True)
        assert await cache_repository.get(NEW_KEY) == NEW_VALUE
        await cache_repository.set(NEW_KEY, NEW_VALUE_EXTRA, nx=False)
        assert await cache_repository.get(NEW_KEY) == NEW_VALUE_EXTRA

    @classmethod
    async def test_ttl(cls, cache_repository: CacheRepositoryProtocol) -> None:
        """
        Тестируем метод `set` с параметром `expire` и функцию `get_with_ttl`.

        Потенциально хрупкий тест из-за возможных задержек ответа от Redis.
        """
        for key, expected_value in CACHE_DATA.items():
            ttl_ts, actual_value = await cache_repository.get_with_ttl(key)
            assert ttl_ts, -1
            assert actual_value == expected_value
        await cache_repository.set(NEW_KEY, NEW_VALUE, EXPIRE)
        assert await cache_repository.get(NEW_KEY) == NEW_VALUE
        await asyncio.sleep(EXPIRE + 1)
        assert await cache_repository.get(NEW_KEY) is None

    @staticmethod
    async def test_incr(cache_repository: CacheRepositoryProtocol) -> None:
        """
        Тестируем метод `incr`.
        """
        assert await cache_repository.get(INT_KEY) == str(INT_VALUE)
        await cache_repository.incr(INT_KEY)
        assert await cache_repository.get(INT_KEY) == str(INT_VALUE + 1)

    @staticmethod
    async def test_decr(cache_repository: CacheRepositoryProtocol) -> None:
        """
        Тестируем метод `decr`.
        """
        assert await cache_repository.get(INT_KEY) == str(INT_VALUE)
        await cache_repository.decr(INT_KEY)
        assert await cache_repository.get(INT_KEY) == str(INT_VALUE - 1)

    @classmethod
    async def test_clear(cls, cache_repository: CacheRepositoryProtocol) -> None:
        """
        Тестируем метод `clear`.
        """
        assert await cache_repository.get(STR_KEY) == STR_VALUE
        assert 1 == await cache_repository.clear(key=STR_KEY)
        assert await cache_repository.get(STR_KEY) is None
        for key, expected_value in NAMESPACE_CACHE_DATA.items():
            assert await cache_repository.get(key) == expected_value
        assert 2 == await cache_repository.clear(namespace=NAMESPACE)
        for key in NAMESPACE_CACHE_DATA.keys():
            assert await cache_repository.get(key) is None
