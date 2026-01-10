"""
Module containing the in-memory cache repository.
"""

from typing import Self

from fastapi_cache.backends.inmemory import InMemoryBackend, Value
from overrides import override


class InMemoryCacheRepository(InMemoryBackend):
    """
    In-memory cache repository.
    """

    @override(check_signature=False)
    def _get(self, key: str) -> Value | None:
        """
        Get the internal value.

        Parent method works incorrectly because it is not designed for the correct `set` method logic.
        """
        v = self._store.get(key)
        if v:
            if v.ttl_ts == -1 or v.ttl_ts >= self._now:
                return v
            else:
                del self._store[key]
        return None

    @override(check_signature=False)
    async def set(self: Self, key: str, value: str, expire: int | None = None, nx: bool = False) -> None:
        """
        Set a value.

        Parent method works incorrectly because when `expire` is absent it should be set to `-1`.
        The old logic makes the method behave differently than `RedisBackend`.
        """
        async with self._lock:
            ttl_ts = self._now + expire if expire is not None else -1
            existing_value = self._get(key)
            if not nx or existing_value is None:
                self._store[key] = Value(value, ttl_ts)  # type: ignore

    async def incr(self: Self, key: str, amount: int = 1) -> int:
        """
        Increment a value.
        """
        v = self._get(key)
        if v is None:
            n_value = amount
            await self.set(key, str(amount))
            return n_value
        n_value = int(v.data) + amount
        await self.set(key, str(n_value))
        return n_value

    async def decr(self: Self, key: str, amount: int = 1) -> int:
        """
        Decrement a value.
        """
        return await self.incr(key, -amount)
