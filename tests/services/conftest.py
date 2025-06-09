"""
Модуль, содержащий фикстуры для тестов сервисов.
"""

from collections.abc import AsyncIterator

import pytest
from fast_clean.db import Base, SessionManagerProtocol, make_async_engine, make_async_session_factory
from fast_clean.services.cryptography import (
    AesCbcCryptographyService,
    AesGcmCryptographyService,
    CryptographyServiceProtocol,
)
from fast_clean.services.lock import LockServiceProtocol, RedisLockService
from fast_clean.services.seed import SeedService
from fast_clean.services.transaction import TransactionService

from redis import asyncio as aioredis
from tests.settings import SettingsSchema


@pytest.fixture
async def cryptography_service(settings: SettingsSchema, request: pytest.FixtureRequest) -> CryptographyServiceProtocol:
    """
    Получаем репозиторий кеша.
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
    Получаем сервис распределенной блокировки.
    """
    return RedisLockService(aioredis.from_url(url=str(settings.redis_dsn), decode_responses=True))


@pytest.fixture
async def seed_service(settings: SettingsSchema, session_manager: SessionManagerProtocol) -> AsyncIterator[SeedService]:
    """
    Получаем сервис для загрузки данных из файлов.
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
    Получаем сервис транзакций.
    """
    async with make_async_session_factory(settings.db.dsn)() as session:
        return TransactionService(session)
