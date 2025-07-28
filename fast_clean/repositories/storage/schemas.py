"""
Модуль, содержащий схемы файлового хранилища.
"""

from pathlib import Path

from pydantic import BaseModel


class S3StorageParamsSchema(BaseModel):
    """
    Параметры настроек для S3Storage.
    """

    """
    Параметры настроек для S3Storage.
    """

    endpoint: str
    aws_secret_access_key: str
    aws_access_key_id: str
    port: int
    bucket: str
    secure: bool = True
    region_name: str = 'us-east-1'


class LocalStorageParamsSchema(BaseModel):
    """
    Параметры настроек для LocalStorage.
    """

    path: Path


StorageParamsSchema = S3StorageParamsSchema | LocalStorageParamsSchema
