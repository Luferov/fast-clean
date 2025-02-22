"""
Модуль, содержащий настройки тестов.
"""

from pathlib import Path

from fast_clean.settings import CoreDbSettingsSchema, CoreKafkaSettingsSchema, CoreS3SettingsSchema
from pydantic import BaseModel, RedisDsn
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


class StorageSettingsSchema(BaseModel):
    """
    Настройки для хранилища.
    """

    dir: Path = Path(__file__).resolve().parent / 'storage'
    s3: CoreS3SettingsSchema


class SettingsSchema(BaseSettings):
    """
    Настройки тестов.
    """

    base_dir: Path = Path(__file__).resolve().parent
    secret_key: str

    redis_dsn: RedisDsn
    db: CoreDbSettingsSchema
    storage: StorageSettingsSchema
    kafka: CoreKafkaSettingsSchema

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
