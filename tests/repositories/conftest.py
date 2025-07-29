"""
Модуль, содержащий фикстуры для тестов репозиториев.
"""

import asyncio
import dataclasses
import io
import os
import shutil
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from itertools import groupby
from typing import cast

import aiobotocore
import aiobotocore.session
import pytest
import sqlalchemy as sa
from aiokafka import AIOKafkaConsumer
from botocore.exceptions import ClientError
from fast_clean.db import (
    BaseUUID as Base,
)
from fast_clean.db import (
    SessionManagerImpl,
    make_async_engine,
    make_async_session_factory,
)
from fast_clean.repositories.cache import (
    CacheRepositoryProtocol,
    InMemoryCacheRepository,
    RedisCacheRepository,
)
from fast_clean.repositories.settings import EnvSettingsRepository, SettingsRepositoryProtocol
from fast_clean.repositories.storage import (
    LocalStorageParamsSchema,
    LocalStorageRepository,
    S3StorageParamsSchema,
    S3StorageRepository,
    StorageRepositoryProtocol,
)
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from tests.settings import SettingsSchema

from .enums import CrudModelTypeEnum
from .models import CrudChildAModel, CrudChildBModel, CrudParentModel
from .repositories import (
    ModelDbRepository,
    ModelInMemoryRepository,
    ModelRepositoryProtocol,
)
from .schemas import CrudParentModelReadSchema, DirectorySchema, FileSchema, MessageSchema
from .settings import ServiceSettingsSchema, SettingsTest
from .utils import walk_path


@pytest.fixture
async def cache_repository(
    settings: SettingsSchema, request: pytest.FixtureRequest
) -> AsyncIterator[CacheRepositoryProtocol]:
    """
    Получаем репозиторий кеша.
    """
    repository_kind, data = request.param
    match repository_kind:
        case 'in_memory':
            repository = InMemoryCacheRepository()
            for k, v in data.items():
                await repository.set(k, v)
            yield cast(CacheRepositoryProtocol, repository)
        case 'redis':
            if not settings.cache.redis:
                pytest.skip('Redis not configured in settings')

            redis_dsn = str(settings.cache.redis.dsn)
            try:
                redis_client = aioredis.from_url(redis_dsn, decode_responses=True)
                await redis_client.ping()
            except Exception:
                pytest.skip(f'Redis not available at {redis_dsn}')

            if settings.cache.redis:
                for k, v in data.items():
                    await redis_client.set(k, v)
                try:
                    yield cast(CacheRepositoryProtocol, RedisCacheRepository(redis_client))
                finally:
                    await redis_client.flushall()


@contextmanager
def make_in_memory_crud_repository(
    models_to_create: list[CrudParentModelReadSchema],
) -> Iterator[ModelInMemoryRepository]:
    """
    Создаем репозиторий для выполнения операций над моделями в памяти.
    """
    repository = ModelInMemoryRepository()
    repository.models = {model.id: model for model in models_to_create}
    yield repository


async def create_models(session: AsyncSession, models_to_create: list[CrudParentModelReadSchema]) -> None:
    """
    Создаем модели в базе данных.
    """
    for model_type, models in groupby(sorted(models_to_create, key=lambda k: k.type), lambda k: k.type):
        match model_type:
            case CrudModelTypeEnum.PARENT:
                statement = sa.insert(CrudParentModel)
                await session.execute(statement, [m.model_dump() for m in models])
            case CrudModelTypeEnum.CHILD_A | CrudModelTypeEnum.CHILD_B:
                for model in models:
                    parent_statement = sa.insert(CrudParentModel).values(
                        model.model_dump(include={'id', 'str_column', 'int_column', 'type'})
                    )
                    await session.execute(parent_statement)
                    child_model = CrudChildAModel if model_type == CrudModelTypeEnum.CHILD_A else CrudChildBModel
                    child_statement = sa.insert(child_model).values(
                        model.model_dump(exclude={'str_column', 'int_column', 'type'})
                    )
                    await session.execute(child_statement)


@asynccontextmanager
async def make_db_crud_repository(
    settings: SettingsSchema, models_to_create: list[CrudParentModelReadSchema]
) -> AsyncIterator[ModelDbRepository]:
    """
    Создаем репозиторий для выполнения операций над моделями в базе данных.
    """
    async_engine = make_async_engine(settings.db.dsn)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        async with make_async_session_factory(settings.db.dsn)() as session:
            await create_models(session, models_to_create)
            yield ModelDbRepository(SessionManagerImpl(session))
    finally:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def crud_repository(
    settings: SettingsSchema, request: pytest.FixtureRequest
) -> AsyncIterator[ModelRepositoryProtocol]:
    """
    Получаем репозиторий для выполнения CRUD операций над моделями.
    """
    repository_kind, models_to_create = request.param
    match repository_kind:
        case 'in_memory':
            with make_in_memory_crud_repository(models_to_create) as repository:
                yield repository
        case 'db':
            async with make_db_crud_repository(settings, models_to_create) as repository:
                yield repository
        case _:
            raise NotImplementedError()


@pytest.fixture
async def settings_repository(request: pytest.FixtureRequest) -> AsyncIterator[SettingsRepositoryProtocol]:
    """
    Получаем репозиторий настроек.
    """
    service: ServiceSettingsSchema
    _, service = request.param
    repository = EnvSettingsRepository()
    repository.settings = [SettingsTest(service=service)]
    yield repository


@contextmanager
def make_local_storage_repository(
    settings: SettingsSchema, directory: DirectorySchema
) -> Iterator[StorageRepositoryProtocol]:
    """
    Создаем репозиторий локального файлового хранилища.
    """
    for path, item in walk_path(directory, settings.storage.dir):
        if isinstance(item, DirectorySchema):
            if not path.exists():
                os.mkdir(path)
        else:
            path.write_bytes(item.content)
    try:
        yield LocalStorageRepository(LocalStorageParamsSchema(path=settings.storage.dir))
    finally:
        shutil.rmtree(settings.storage.dir, ignore_errors=True)


@asynccontextmanager
async def make_s3_storage_repository(
    settings: SettingsSchema, directory: DirectorySchema
) -> AsyncIterator[StorageRepositoryProtocol]:
    """
    Создаем репозиторий хранилища S3.
    """
    params = settings.storage.s3
    session = aiobotocore.session.get_session()
    protocol = 'https' if settings.storage.s3.secure else 'http'
    endpoint_url = f'{protocol}://{params.endpoint}:{params.port}'
    async with session.create_client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=params.aws_access_key_id,
        aws_secret_access_key=params.aws_secret_access_key,
        region_name='',
    ) as client:
        try:
            await client.head_bucket(Bucket=params.bucket)
        except ClientError as e:
            if e.response.get('Error', {}).get('Code') == '404':
                await client.create_bucket(Bucket=params.bucket)
            else:
                raise
        for path, item in walk_path(directory):
            if isinstance(item, FileSchema):
                data = io.BytesIO(item.content)
                await client.put_object(
                    Bucket=params.bucket,
                    Key=str(path),
                    Body=data,
                    ContentLength=len(item.content),
                )
        try:
            yield S3StorageRepository(S3StorageParamsSchema.model_validate(settings.storage.s3.model_dump()))
            for path, item in walk_path(directory):
                if isinstance(item, FileSchema):
                    await client.delete_object(Bucket=params.bucket, Key=str(path))
        finally:
            await client.delete_bucket(Bucket=params.bucket)


@pytest.fixture
async def storage_repository(
    settings: SettingsSchema, request: pytest.FixtureRequest
) -> AsyncIterator[StorageRepositoryProtocol]:
    """
    Получаем репозиторий файлового хранилища.
    """
    repository_kind, directory = request.param
    match repository_kind:
        case 'local':
            with make_local_storage_repository(settings, directory) as storage:
                yield storage
        case 's3':
            async with make_s3_storage_repository(settings, directory) as storage:
                yield storage
        case _:
            raise NotImplementedError()


@asynccontextmanager
async def consume_kafka_message(settings: SettingsSchema, topic: str) -> AsyncIterator[MessageSchema]:
    """
    Потребляем сообщение из Kafka.
    """
    consumer = AIOKafkaConsumer(topic, bootstrap_servers=settings.kafka.bootstrap_servers, auto_offset_reset='earliest')
    await consumer.start()
    try:
        message = await asyncio.wait_for(consumer.getone(), timeout=5.0)
        yield MessageSchema.model_validate(dataclasses.asdict(message))
    finally:
        await consumer.stop()
