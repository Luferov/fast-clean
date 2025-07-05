"""
Модуль, содержащий настройки.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, ClassVar, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, RedisDsn, model_validator
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict
from typing_extensions import Unpack


class CoreDbSettingsSchema(BaseModel):
    """
    Схема настроек базы данных.
    """

    provider: str = 'postgresql+psycopg_async'

    host: str
    port: int
    user: str
    password: str
    name: str

    scheme: str = 'public'

    @property
    def dsn(self: Self) -> str:
        """
        DSN подключения к базе данных.
        """
        return f'{self.provider}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'


class CoreCacheSettingsSchema(BaseModel):
    """
    Схема настроек кеша.
    """

    provider: Literal['in_memory', 'redis'] = 'in_memory'

    prefix: str


class CoreS3SettingsSchema(BaseModel):
    """
    Схема настроек S3.
    """

    endpoint: str
    endpoint_url: str
    access_key: str
    secret_key: str
    port: int
    bucket: str
    secure: bool = False


class CoreStorageSettingsSchema(BaseModel):
    """
    Схема настроек хранилища.
    """

    provider: Literal['local', 's3'] = 'local'

    dir: Path = Path(__file__).resolve().parent.parent / 'storage'
    s3: CoreS3SettingsSchema | None = None


class CoreElasticsearchSettingsSchema(BaseModel):
    """
    Схема настроек Elasticsearch.
    """

    host: str
    port: int
    scheme: str
    username: str
    password: str
    cluster_name: str

    cacert: str | None = None
    security: bool = False
    ssl: bool = False


class CoreSearchSettingsSchema(BaseModel):
    """
    Схема настроек движка поиска.
    """

    provider: Literal['elasticsearch', 'open_search'] = 'elasticsearch'
    elasticsearch: CoreElasticsearchSettingsSchema | None = None


class CoreKafkaSettingsSchema(BaseModel):
    """
    Схема настроек Kafka.
    """

    bootstrap_servers: str
    group_id: str
    credentials: Literal['SSL', 'SASL'] | None = None
    # For SSL
    cert_file: str | None = None
    ca_file: str | None = None
    key_file: str | None = None
    password: str | None = None
    # For SASL
    broker_username: str | None = None
    broker_password: str | None = None

    @model_validator(mode='after')
    def validate_credentials(self: Self) -> Self:
        """
        Проверяем на правильность заполнение параметров для авторизации.
        """
        match self.credentials:
            case 'SSL':
                for field in ('ca_file', 'cert_file', 'key_file'):
                    assert bool(getattr(self, field)), f'{field} must be set when credentials={self.credentials}'
            case 'SASL':
                for field in ('broker_username', 'broker_password'):
                    assert bool(getattr(self, field)), f'{field} must be set when credentials={self.credentials}'
            case _:
                ...
        return self


class CoreServiceSettingsSchema(BaseModel):
    """
    Схема настроек доступа к сервису.
    """

    host: str
    user: str | None = None
    password: str | None = None


class CoreTopicSettingsSchema(BaseModel):
    """
    Схема настроек топика.
    """

    name: str
    auto_offset_reset: Literal['latest', 'earliest', 'none'] = 'latest'


class BaseSettingsSchema(PydanticBaseSettings):
    """
    Схема настроек с возможностью поиска через репозиторий.
    """

    descendant_types: ClassVar[list[type[BaseSettingsSchema]]] = []

    def __init_subclass__(cls, **kwargs: Unpack[ConfigDict]) -> None:
        """
        Добавляем настройки в репозиторий.
        """
        cls.descendant_types.append(cls)

        return super().__init_subclass__(**kwargs)


class CoreSettingsSchema(BaseSettingsSchema):
    """
    Схема базовых настроек приложения.
    """

    debug: bool
    base_url: str
    base_dir: Path = Path(os.getcwd())
    secret_key: str
    cors_origins: Annotated[list[str], Field(default_factory=list)]
    redis_dsn: RedisDsn | None = None
    sentry_dsn: str | None = None

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_nested_delimiter='__',
        case_sensitive=False,
        extra='ignore',
    )
