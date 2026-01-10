"""
Module containing file storage schemas.
"""

from pathlib import Path

from pydantic import BaseModel


class S3StorageParamsSchema(BaseModel):
    """
    Settings parameters for S3Storage.
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
    Settings parameters for LocalStorage.
    """

    path: Path


StorageParamsSchema = S3StorageParamsSchema | LocalStorageParamsSchema
