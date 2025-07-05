"""
Модуль, содержащий репозиторий хранилища S3.
"""

import io
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Self

import aiohttp
import miniopy_async
from miniopy_async.error import S3Error

from .reader import AiohttpStreamReader, StreamReaderProtocol, StreamReadProtocol
from .schemas import S3StorageParamsSchema


class S3StorageRepository:
    """
    Репозиторий хранилища S3.
    """

    def __init__(self: Self, params: S3StorageParamsSchema):
        self.params = params
        self.bucket = self.params.bucket
        self.client = miniopy_async.Minio(  # type: ignore
            f'{self.params.endpoint}:{self.params.port}',
            access_key=self.params.access_key,
            secret_key=self.params.secret_key,
            secure=self.params.secure,
        )

    async def exists(self: Self, path: str | Path) -> bool:
        """
        Проверяем существует ли файл.
        """
        try:
            await self.client.stat_object(self.bucket, self.get_str_path(path))
            return True
        except S3Error:
            return False

    async def listdir(self: Self, path: str | Path) -> list[str]:
        """
        Получаем список файлов и директорий в заданной директории.
        """
        str_path = self.get_str_path(path)
        if not str_path or str_path[-1] != '/':
            str_path += '/'
        objects = await self.client.list_objects(self.bucket, prefix=str_path if str_path != '/' else None)
        return [str(obj.object_name) for obj in objects] if objects else []

    async def is_file(self: Self, path: str | Path) -> bool:
        """
        Проверяем находится ли файл по пути.
        """
        return not await self.is_dir(path)

    async def is_dir(self: Self, path: str | Path) -> bool:
        """
        Проверяем находится ли директория по пути.
        """
        return len(await self.listdir(path)) > 0

    async def read(self: Self, path: str | Path) -> bytes:
        """
        Читаем содержимое файла.
        """
        async with aiohttp.ClientSession() as session:
            response: aiohttp.ClientResponse = await self.client.get_object(
                self.bucket, self.get_str_path(path), session
            )
            return await response.read()

    @asynccontextmanager
    async def stream_read(self: Self, path: str | Path) -> AsyncGenerator[StreamReaderProtocol, None]:
        """
        Читаем содержимое файла в потоковом режиме.
        """
        async with aiohttp.ClientSession() as session:
            reader = await self.client.get_object(self.bucket, self.get_str_path(path), session)
            yield AiohttpStreamReader(reader)

    async def write(self: Self, path: str | Path, content: str | bytes) -> None:
        """
        Создаем файл или переписываем существующий.
        """
        content = content.encode('utf-8') if isinstance(content, str) else content
        data = io.BytesIO(content)
        await self.client.put_object(self.bucket, self.get_str_path(path), data, len(content))

    async def stream_write(
        self: Self,
        path: str | Path,
        stream: StreamReadProtocol,
        length: int = -1,
        part_size: int = 0,
    ) -> None:
        """
        Создаем файл или переписываем существующий в потоковом режиме.
        """
        await self.client.put_object(self.bucket, self.get_str_path(path), stream, length=length, part_size=part_size)

    async def delete(self: Self, path: str | Path) -> None:
        """
        Удаляем файл.
        """
        await self.client.remove_object(self.bucket, self.get_str_path(path))

    @staticmethod
    def get_str_path(path: str | Path) -> str:
        """
        Получаем путь в виде строки.
        """
        if isinstance(path, Path):
            return '/' if path == Path('') else str(path)
        return path
