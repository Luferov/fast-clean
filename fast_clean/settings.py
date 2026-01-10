"""
Module containing settings.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import ClassVar, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, RedisDsn
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict
from typing_extensions import Unpack

from fast_clean.schemas import BasicAuthSchema, BearerTokenAuthSchema


class CoreDbSettingsSchema(BaseModel):
    """
    Database settings schema.
    """

    provider: str = 'postgresql+psycopg_async'

    host: str
    port: int
    user: str
    password: str
    name: str

    echo: bool = False
    pool_pre_ping: bool = True
    disable_prepared_statements: bool = True
    scheme: str = 'public'

    @property
    def dsn(self: Self) -> str:
        """
        Database connection DSN.
        """
        return f'{self.provider}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'


class CoreRedisSettingsSchema(BaseModel):
    dsn: RedisDsn


class CoreCacheSettingsSchema(BaseModel):
    """
    Cache settings schema.
    """

    provider: Literal['in_memory', 'redis'] = 'in_memory'

    prefix: str

    redis: CoreRedisSettingsSchema | None = None


class CoreS3SettingsSchema(BaseModel):
    """
    S3 settings schema.
    """

    endpoint: str
    aws_access_key_id: str
    aws_secret_access_key: str
    port: int
    bucket: str
    secure: bool = False


class CoreStorageSettingsSchema(BaseModel):
    """
    Storage settings schema.
    """

    provider: Literal['local', 's3'] = 'local'

    dir: Path = Path(__file__).resolve().parent.parent / 'storage'
    s3: CoreS3SettingsSchema | None = None


class CoreElasticsearchSettingsSchema(BaseModel):
    """
    Elasticsearch settings schema.
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
    Search engine settings schema.
    """

    provider: Literal['elasticsearch', 'open_search'] = 'elasticsearch'
    elasticsearch: CoreElasticsearchSettingsSchema | None = None


class CoreServiceSettingsSchema(BaseModel):
    """
    Service access settings schema.
    """

    host: HttpUrl

    auth: BasicAuthSchema | BearerTokenAuthSchema | None = Field(None, discriminator='type')
    """
    Authentication.
    """
    username: str | None = Field(None, deprecated=True)
    password: str | None = Field(None, deprecated=True)
    """
    Basic Auth authentication.
    """

    verify: bool = True
    retries: int = 3
    """
    Three attempts to establish a connection.
    """


class BaseSettingsSchema(PydanticBaseSettings):
    """
    Settings schema with repository-based search.
    """

    descendant_types: ClassVar[list[type[BaseSettingsSchema]]] = []

    def __init_subclass__(cls, **kwargs: Unpack[ConfigDict]) -> None:
        """
        Add settings to the repository.
        """
        cls.descendant_types.append(cls)

        return super().__init_subclass__(**kwargs)


class CoreSettingsSchema(BaseSettingsSchema):
    """
    Base application settings schema.
    """

    debug: bool
    title: str
    base_url: str
    base_dir: Path = Path(os.getcwd())
    secret_key: str
    cors_origins: list[str]
    environment: Literal['dev', 'test', 'prod']
    redis_dsn: RedisDsn | None = None
    sentry_dsn: str | None = None

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_nested_delimiter='__',
        case_sensitive=False,
        extra='ignore',
    )
