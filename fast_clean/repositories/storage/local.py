"""
Module containing the local file storage repository.
"""

import asyncio
import os
from collections.abc import AsyncGenerator, AsyncIterator, Awaitable, Callable
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
    Local file storage repository.
    """

    def __init__(self: Self, params: LocalStorageParamsSchema) -> None:
        self.work_dir = Path(params.path)
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)
        self.logger = getLogger(__name__)

    async def __aenter__(self: Self) -> Self:
        """
        Enter the context manager.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb): ...

    async def exists(self: Self, path: str | Path) -> bool:
        """
        Check whether the file exists.
        """
        path = self.work_dir / path
        return await aos.path.exists(path)

    async def listdir(self: Self, path: str | Path) -> list[str]:
        """
        Get a list of files and directories in the specified directory.
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
        Check whether a file exists at the path.
        """
        path = self.work_dir / path
        return await aos.path.isfile(path)

    async def is_dir(self: Self, path: str | Path) -> bool:
        """
        Check whether a directory exists at the path.
        """
        path = self.work_dir / path
        return await aos.path.isdir(path)

    async def read(self: Self, path: str | Path) -> bytes:
        """
        Read file contents.
        """
        path = self.work_dir / path
        async with open(path, 'rb') as f:
            return await f.read()

    @asynccontextmanager
    async def stream_read(self: Self, path: str | Path) -> AsyncGenerator[StreamReaderProtocol, None]:
        """
        Read file contents in streaming mode.
        """
        path = self.work_dir / path
        async with open(path, 'rb') as f:
            yield AiofilesStreamReader(f)

    async def straming_read(self: Self, path: str | Path) -> AsyncIterator[bytes]:
        path = self.work_dir / path
        async with open(path, 'rb') as f:
            async for chunk in f:
                yield chunk

    async def write(self: Self, path: str | Path, content: str | bytes) -> None:
        """
        Create a file or overwrite an existing one.
        """
        path = self.work_dir / path
        await aos.makedirs(path.parent, exist_ok=True)
        async with open(path, mode='wb') as f:
            await f.write(content.encode('utf-8') if isinstance(content, str) else content)

    async def stream_write(
        self: Self,
        path: str | Path,
        stream: StreamReadProtocol,
    ) -> None:
        """
        Create a file or overwrite an existing one in streaming mode.
        """
        part_size = 1024 * 1024
        path = self.work_dir / path
        await aos.makedirs(path.parent, exist_ok=True)
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
        Delete a file.
        """
        path = self.work_dir / path
        await aos.remove(path)
