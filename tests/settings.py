"""
Module containing test settings.
"""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, RedisDsn
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

from fast_clean.settings import CoreDbSettingsSchema, CoreS3SettingsSchema


class CoreRedisSettingsSchema(BaseModel):
    dsn: RedisDsn


class CoreCacheSettingsSchema(BaseModel):
    """
    Cache settings schema.
    """

    provider: Literal['in_memory', 'redis'] = 'in_memory'

    prefix: str

    redis: CoreRedisSettingsSchema | None = None


class StorageSettingsSchema(BaseModel):
    """
    Storage settings.
    """

    dir: Path = Path(__file__).resolve().parent / 'storage'
    s3: CoreS3SettingsSchema


class SettingsSchema(BaseSettings):
    """
    Test settings.
    """

    base_dir: Path = Path(__file__).resolve().parent
    secret_key: str

    db: CoreDbSettingsSchema
    storage: StorageSettingsSchema
    cache: CoreCacheSettingsSchema

    model_config = SettingsConfigDict(
        env_file='tests/.env',
        env_file_encoding='utf-8',
        env_nested_delimiter='__',
        case_sensitive=False,
        extra='ignore',
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return init_settings, dotenv_settings, env_settings, file_secret_settings
