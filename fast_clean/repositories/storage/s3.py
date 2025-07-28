"""
Модуль содержит имплементация работы с репозиторием по средствам протокола S3.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Self, cast

import aiobotocore
import aiobotocore.session
from aiobotocore.response import StreamingBody
from aiobotocore.session import AioSession
from botocore.exceptions import ClientError

from fast_clean.repositories.storage.schemas import S3StorageParamsSchema

from .reader import AiofilesStreamReader, StreamReaderProtocol, StreamReadProtocol

if TYPE_CHECKING:
    from types_aiobotocore_s3.client import S3Client as AioBaseClient
else:
    from aiobotocore.client import AioBaseClient


class S3StorageRepository:
    """
    Репозиторий хранилища S3 с использованием aiobotocore.
    """

    def __init__(self, params: S3StorageParamsSchema) -> None:
        self.params = params
        self.bucket = self.params.bucket

        self.session: AioSession | None = None
        self.client: AioBaseClient | None = None

        protocol = 'https' if self.params.secure else 'http'
        self.endpoint_url = f'{protocol}://{self.params.endpoint}:{self.params.port}'

    async def __aenter__(self: Self) -> Self:
        self.session = aiobotocore.session.get_session()
        self.client = await self.session.create_client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.params.aws_access_key_id,
            aws_secret_access_key=self.params.aws_secret_access_key,
            region_name=self.params.region_name,
        ).__aenter__()
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        """
        Выход из контектсного менеджера сессии.
        """
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
            self.client = None
            self.session = None

    async def exists(self: Self, path: str | Path) -> bool:
        assert self.client
        key = self.get_str_path(path)
        if key == '':
            key = '/'
        try:
            await self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False

    async def listdir(self: Self, path: str | Path) -> list[str]:
        """
        Получаем список файлов и директорий в указанной лиректории.
        """
        assert self.client
        prefix = self.get_str_path(path)
        if prefix and not prefix.endswith('/'):
            prefix += '/'
        objects = []
        paginator = self.client.get_paginator('list_objects_v2')
        async for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix, Delimiter='/'):
            if 'Contents' in page:
                objects.extend([obj.get('Key') for obj in page['Contents'] if obj.get('Key') != prefix])
            if 'CommonPrefixes' in page:
                objects.extend([folder.get('Prefix') for folder in page['CommonPrefixes']])
        return objects

    async def is_file(self: Self, path: str | Path) -> bool:
        """
        Проверяем, является ли путь файлом.
        """
        return await self.exists(path)

    async def is_dir(self: Self, path: str | Path) -> bool:
        """
        Проверяем, является ли путь дирректорией.
        """
        assert self.client
        prefix = self.get_str_path(path)
        if prefix != '' and not prefix.endswith('/'):
            prefix += '/'
        response = await self.client.list_objects_v2(
            Bucket=self.bucket,
            Prefix=prefix,
            MaxKeys=1,
            Delimiter='/',
        )
        return 'Contents' in response or 'CommonPrefixes' in response

    async def read(self: Self, path: str | Path) -> bytes:
        """
        Читаем содержимое файла.
        """
        assert self.client
        key = self.get_str_path(path)
        response = await self.client.get_object(Bucket=self.bucket, Key=key)
        async with response['Body'] as stream:
            return await stream.read()

    async def write(self: Self, path: str | Path, content: str | bytes) -> None:
        """
        Создаем файл или перезаписываем существующий.
        """
        assert self.client
        key = self.get_str_path(path)
        content = content.encode('utf-8') if isinstance(content, str) else content
        await self.client.put_object(Bucket=self.bucket, Key=key, Body=content)

    @asynccontextmanager
    async def stream_read(self: Self, path: str | Path) -> AsyncIterator[StreamReaderProtocol]:
        """
        Читаем содержимое в потоковом режиме.
        """
        assert self.client
        key = self.get_str_path(path)
        response = await self.client.get_object(Bucket=self.bucket, Key=key)
        yield AiofilesStreamReader(response['Body'])

    async def straming_read(self: Self, path: str | Path) -> AsyncIterator[bytes]:
        assert self.client
        key = self.get_str_path(path)
        response = await self.client.get_object(Bucket=self.bucket, Key=key)
        async for chunk in response['Body']:
            yield chunk

    async def stream_write(self: Self, path: str | Path, stream: StreamReadProtocol) -> None:
        """
        Создаем поток на запись файла и перезаписываем существующий, если он есть.
        """
        assert self.client
        await self.client.put_object(Bucket=self.bucket, Key=self.get_str_path(path), Body=cast(StreamingBody, stream))

    async def delete(self: Self, path: str | Path) -> None:
        """
        Удаление файла.
        """
        assert self.client
        key = self.get_str_path(path)
        await self.client.delete_object(Bucket=self.bucket, Key=key)

    @staticmethod
    def get_str_path(path: str | Path) -> str:
        """
        Получаем путь в виде строки.
        """
        if isinstance(path, Path):
            return '' if path == Path('') else str(path)
        return path
