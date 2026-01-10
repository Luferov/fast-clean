"""
Module containing tests for the distributed lock service.
"""

import asyncio
import random
from dataclasses import dataclass

import pytest

from fast_clean.exceptions import LockError
from fast_clean.services import LockServiceProtocol


@dataclass
class Resource:
    """
    Lockable resource.
    """

    is_locked: bool = False


class TestLockService:
    """
    Tests for the distributed lock service.
    """

    @classmethod
    async def test_lock_resource(cls, lock_service: LockServiceProtocol) -> None:
        """
        Test the `lock` method to lock a shared resource.
        """
        resource = Resource()
        await asyncio.gather(*[cls.lock_resource(lock_service, resource) for _ in range(5)])

    @staticmethod
    async def test_lock_timeouts(lock_service: LockServiceProtocol) -> None:
        """
        Test the `timeouts` parameter of the `lock` method.
        """
        name = 'test_lock_timeouts'
        with pytest.raises(LockError):
            async with lock_service.lock(name, timeout=5):
                with pytest.raises(LockError):
                    async with lock_service.lock(name, blocking_timeout=2.5):
                        pass
                await asyncio.sleep(2.5)
                async with lock_service.lock(name, blocking_timeout=0.5):
                    pass

    @staticmethod
    async def lock_resource(lock_service: LockServiceProtocol, resource: Resource) -> None:
        """
        Lock and modify the resource.
        """
        async with lock_service.lock('lock_resource'):
            assert not resource.is_locked
            resource.is_locked = True
            await asyncio.sleep(random.randint(250, 750) / 1000)
            resource.is_locked = False
