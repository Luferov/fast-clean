"""
Модуль, содержащий схемы файлового хранилища.
"""

from pathlib import Path

from pydantic import BaseModel


class S3StorageParamsSchema(BaseModel):
    """
    Параметры настроек для S3Storage.
    """

    endpoint: str
    access_key: str
    secret_key: str
    port: int
    bucket: str
    secure: bool = False


class LocalStorageParamsSchema(BaseModel):
    """
    Параметры настроек для LocalStorage.
    """

    path: Path


StorageParamsSchema = S3StorageParamsSchema | LocalStorageParamsSchema
