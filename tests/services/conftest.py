"""
Module containing fixtures for service tests.
"""

from collections.abc import AsyncIterator

import pytest
from redis import asyncio as aioredis

from fast_clean.db import Base, SessionManagerProtocol, make_async_engine, make_async_session_factory
from fast_clean.services.cryptography import (
    AesCbcCryptographyService,
    AesGcmCryptographyService,
    CryptographyServiceProtocol,
)
from fast_clean.services.lock import LockServiceProtocol, RedisLockService
from fast_clean.services.seed import SeedService
from fast_clean.services.transaction import TransactionService
from tests.settings import SettingsSchema


@pytest.fixture
async def cryptography_service(settings: SettingsSchema, request: pytest.FixtureRequest) -> CryptographyServiceProtocol:
    """
    Get the cache repository.
    """
    match request.param:
        case 'aes_gcm':
            return AesGcmCryptographyService(settings.secret_key)
        case 'aes_cbc':
            return AesCbcCryptographyService(settings.secret_key)
        case _:
            raise NotImplementedError()


@pytest.fixture
def lock_service(settings: SettingsSchema) -> LockServiceProtocol:
    """
    Get the distributed lock service.
    """
    if not settings.cache.redis:
        pytest.skip('Redis not configured in settings')
    return RedisLockService(aioredis.from_url(url=str(settings.cache.redis.dsn), decode_responses=True))  # type: ignore


@pytest.fixture
async def seed_service(settings: SettingsSchema, session_manager: SessionManagerProtocol) -> AsyncIterator[SeedService]:
    """
    Get the service for loading data from files.
    """
    async_engine = make_async_engine(settings.db.dsn)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield SeedService(session_manager)
    finally:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def transaction_service(settings: SettingsSchema) -> TransactionService:
    """
    Get the transaction service.
    """
    async with make_async_session_factory(settings.db.dsn)() as session:
        return TransactionService(session)
