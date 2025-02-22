"""
Модуль, содержащий репозиторий локального файлового хранилища.
"""

import asyncio
import os
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from logging import getLogger
from pathlib import Path
from typing import Self, cast

from aiofiles import open
from aiofiles import os as aos

from .reader import AiofilesStreamReader, StreamReaderProtocol, StreamReadProtocol
from .schemas import LocalStorageParamsSchema


class LocalStorageRepository:
    """
    Репозиторий локального файлового хранилища.
    """

    def __init__(self: Self, params: LocalStorageParamsSchema) -> None:
        self.work_dir = Path(params.path)
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)
        self.logger = getLogger(__name__)

    async def exists(self: Self, path: str | Path) -> bool:
        """
        Проверяем существует ли файл.
        """
        path = self.work_dir / path
        return await aos.path.exists(path)

    async def listdir(self: Self, path: str | Path) -> list[str]:
        """
        Получаем список файлов и директорий в заданной директории.
        """
        paths: list[str] = []
        for item in await aos.listdir(self.work_dir / path):
            item_path = str(Path(path) / item)
            if await aos.path.isdir(self.work_dir / item_path):
                item_path += '/'
            paths.append(item_path)
        return paths

    async def is_file(self: Self, path: str | Path) -> bool:
        """
        Проверяем находится ли файл по пути.
        """
        path = self.work_dir / path
        return await aos.path.isfile(path)

    async def is_dir(self: Self, path: str | Path) -> bool:
        """
        Проверяем находится ли директория по пути.
        """
        path = self.work_dir / path
        return await aos.path.isdir(path)

    async def read(self: Self, path: str | Path) -> bytes:
        """
        Читаем содержимое файла.
        """
        path = self.work_dir / path
        async with open(path, 'rb') as f:
            return await f.read()

    @asynccontextmanager
    async def stream_read(self: Self, path: str | Path) -> AsyncGenerator[StreamReaderProtocol, None]:
        """
        Читаем содержимое файла в потоковом режиме.
        """
        path = self.work_dir / path
        async with open(path, 'rb') as f:
            yield AiofilesStreamReader(f)

    async def write(self: Self, path: str | Path, content: str | bytes) -> None:
        """
        Создаем файл или переписываем существующий.
        """
        path = self.work_dir / path
        await aos.makedirs(path.parent, exist_ok=True)
        async with open(path, mode='wb') as f:
            await f.write(content.encode('utf-8') if isinstance(content, str) else content)

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
        if length != -1:
            self.logger.warning('Параметр length не используется для LocalStorage.')
        part_size = part_size or 1024
        path = self.work_dir / path
        is_co_function = asyncio.iscoroutinefunction(stream.read)
        async with open(path, 'wb') as f:
            while chunk := (
                await cast(Callable[[int], Awaitable[bytes]], stream.read)(part_size)
                if is_co_function
                else cast(Callable[[int], bytes], stream.read)(part_size)
            ):
                await f.write(chunk)

    async def delete(self: Self, path: str | Path) -> None:
        """
        Удаляем файл.
        """
        path = self.work_dir / path
        await aos.remove(path)
