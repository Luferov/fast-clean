"""
Модуль, содержащий зависимости.
"""

import json
from collections.abc import AsyncIterator, Sequence
from typing import Annotated

from fastapi import Depends, Request
from faststream.kafka import KafkaBroker
from flatten_dict import unflatten
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import FormData
from stringcase import snakecase

from .broker import BrokerFactory
from .container import ContainerImpl, ContainerProtocol
from .db import SessionFactory, SessionManagerImpl, SessionManagerProtocol
from .redis import RedisManager
from .repositories import (
    CacheManager,
    CacheRepositoryProtocol,
    LocalStorageParamsSchema,
    S3StorageParamsSchema,
    SettingsRepositoryFactoryImpl,
    SettingsRepositoryFactoryProtocol,
    SettingsRepositoryProtocol,
    SettingsSourceEnum,
    StorageRepositoryFactoryImpl,
    StorageRepositoryFactoryProtocol,
    StorageRepositoryProtocol,
    StorageTypeEnum,
)
from .schemas import PaginationRequestSchema
from .services import (
    CryptographicAlgorithmEnum,
    CryptographyServiceFactoryImpl,
    CryptographyServiceFactoryProtocol,
    CryptographyServiceProtocol,
    LockServiceProtocol,
    RedisLockService,
    SeedServiceImpl,
    SeedServiceProtocol,
    TransactionServiceImpl,
    TransactionServiceProtocol,
)
from .settings import CoreCacheSettingsSchema, CoreKafkaSettingsSchema, CoreSettingsSchema, CoreStorageSettingsSchema

# --- utils ---


def get_container() -> ContainerProtocol:
    """
    Получаем контейнер зависимостей.
    """
    ContainerImpl.init()
    return ContainerImpl()


async def get_nested_form_data(request: Request) -> FormData:
    """
    Получаем форму, позволяющую использовать вложенные словари.
    """
    dot_data = {k.replace('[', '.').replace(']', ''): v for k, v in (await request.form()).items()}
    nested_data = unflatten(dot_data, 'dot')
    for k, v in nested_data.items():
        if isinstance(v, dict):
            nested_data[k] = json.dumps(v)
    return FormData(nested_data)


def get_pagination(page: int | None = None, page_size: int | None = None) -> PaginationRequestSchema:
    """
    Получаем входные данные пагинации.
    """
    return PaginationRequestSchema(page=page or 1, page_size=page_size or 10)


def get_sorting(sorting: str | None = None) -> Sequence[str]:
    """
    Получаем входные данные сортировки.
    """
    if not sorting:
        return []
    return [s[0] + snakecase(s[1:]) if s[0] == '-' else snakecase(s) for s in sorting.split(',')]


Container = Annotated[ContainerProtocol, Depends(get_container)]
NestedFormData = Annotated[FormData, Depends(get_nested_form_data)]
Pagination = Annotated[PaginationRequestSchema, Depends(get_pagination)]
Sorting = Annotated[Sequence[str], Depends(get_sorting)]

# --- repositories ---


def get_settings_repository_factory() -> SettingsRepositoryFactoryProtocol:
    """
    Получаем фабрику репозиториев настроек.
    """
    return SettingsRepositoryFactoryImpl()


SettingsRepositoryFactory = Annotated[SettingsRepositoryFactoryProtocol, Depends(get_settings_repository_factory)]


async def get_settings_repository(settings_repository_factory: SettingsRepositoryFactory) -> SettingsRepositoryProtocol:
    """
    Получаем репозиторий настроек.
    """
    return await settings_repository_factory.make(SettingsSourceEnum.ENV)


SettingsRepository = Annotated[SettingsRepositoryProtocol, Depends(get_settings_repository)]


async def get_settings(settings_repository: SettingsRepository) -> CoreSettingsSchema:
    """
    Получаем настройки.
    """
    return await settings_repository.get(CoreSettingsSchema)


Settings = Annotated[CoreSettingsSchema, Depends(get_settings)]


async def get_broker_repository(settings_repository: SettingsRepository) -> AsyncIterator[KafkaBroker]:
    """
    Получаем репозиторий брокера сообщений.
    """
    kafka_settings = await settings_repository.get(CoreKafkaSettingsSchema)
    yield BrokerFactory.make_static(kafka_settings)


async def get_cache_repository(settings_repository: SettingsRepository) -> CacheRepositoryProtocol:
    """
    Получаем репозиторий кеша.
    """
    settings = await settings_repository.get(CoreSettingsSchema)
    if settings.redis_dsn is not None:
        RedisManager.init(settings.redis_dsn)
    cache_settings = await settings_repository.get(CoreCacheSettingsSchema)
    if CacheManager.cache is None:
        CacheManager.init(cache_settings, RedisManager.redis)
    if CacheManager.cache is not None:
        return CacheManager.cache
    raise ValueError('Cache is not initialized')


def get_storage_repository_factory() -> StorageRepositoryFactoryProtocol:
    """
    Получаем фабрику репозиториев файлового хранилища.
    """
    return StorageRepositoryFactoryImpl()


BrokerRepository = Annotated[KafkaBroker, Depends(get_broker_repository)]
CacheRepository = Annotated[CacheRepositoryProtocol, Depends(get_cache_repository)]
StorageRepositoryFactory = Annotated[StorageRepositoryFactoryProtocol, Depends(get_storage_repository_factory)]


async def get_storage_repository(
    settings_repository: SettingsRepository,
    storage_repository_factory: StorageRepositoryFactory,
) -> StorageRepositoryProtocol:
    """
    Получаем репозиторий файлового хранилища.
    """
    storage_settings = await settings_repository.get(CoreStorageSettingsSchema)
    if storage_settings.provider == 's3' and storage_settings.s3 is not None:
        return await storage_repository_factory.make(
            StorageTypeEnum.S3,
            S3StorageParamsSchema.model_validate(storage_settings.s3.model_dump()),
        )
    elif storage_settings.provider == 'local':
        return await storage_repository_factory.make(
            StorageTypeEnum.LOCAL, LocalStorageParamsSchema(path=storage_settings.dir)
        )
    raise NotImplementedError(f'Storage {storage_settings.provider} not allowed')


StorageRepository = Annotated[StorageRepositoryProtocol, Depends(get_storage_repository)]

# --- db ---


async def get_async_session(settings_repository: SettingsRepository) -> AsyncIterator[AsyncSession]:
    """
    Получаем асинхронную сессию.
    """
    async with SessionFactory.make_async_session_static(settings_repository) as session:
        yield session


Session = Annotated[AsyncSession, Depends(get_async_session)]


def get_session_manager(session: Session) -> SessionManagerProtocol:
    """
    Получаем менеджер сессий.
    """
    return SessionManagerImpl(session)


SessionManager = Annotated[SessionManagerProtocol, Depends(get_session_manager)]

# --- services ---


def get_cryptography_service_factory(settings: Settings) -> CryptographyServiceFactoryProtocol:
    """
    Получаем фабрику сервисов криптографии.
    """
    return CryptographyServiceFactoryImpl(settings.secret_key)


CryptographyServiceFactory = Annotated[CryptographyServiceFactoryProtocol, Depends(get_cryptography_service_factory)]


async def get_cryptography_service(
    cryptography_service_factory: CryptographyServiceFactory,
) -> CryptographyServiceProtocol:
    """
    Получаем сервис криптографии.
    """
    return await cryptography_service_factory.make(CryptographicAlgorithmEnum.AES_GCM)


def get_lock_service(settings: Settings) -> LockServiceProtocol:
    """
    Получаем сервис распределенной блокировки.
    """
    assert settings.redis_dsn is not None
    RedisManager.init(settings.redis_dsn)
    assert RedisManager.redis is not None
    return RedisLockService(RedisManager.redis)


def get_seed_service(session_manager: SessionManager) -> SeedServiceProtocol:
    """
    Получаем сервис для загрузки данных из файлов.
    """
    return SeedServiceImpl(session_manager)


def get_transaction_service(session: Session) -> TransactionServiceProtocol:
    """
    Получаем сервис транзакций.
    """
    return TransactionServiceImpl(session)


CryptographyService = Annotated[CryptographyServiceProtocol, Depends(get_cryptography_service)]
LockService = Annotated[LockServiceProtocol, Depends(get_lock_service)]
SeedService = Annotated[SeedServiceProtocol, Depends(get_seed_service)]
TransactionService = Annotated[TransactionServiceProtocol, Depends(get_transaction_service)]
