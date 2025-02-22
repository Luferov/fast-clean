"""
Модуль, содержащий классы для потокового чтения данных.
"""

from collections.abc import AsyncIterator
from typing import Protocol, Self

from aiofiles.threadpool.binary import AsyncBufferedReader
from aiohttp import ClientResponse

READ_SIZE = 5 * 1024 * 1024


class StreamReadSyncProtocol(Protocol):
    """
    Синхронный протокол потокового чтения данных.
    """

    def read(self: Self, size: int | None = READ_SIZE) -> bytes:
        """
        Читаем данные.
        """
        ...


class StreamReadAsyncProtocol(Protocol):
    """
    Асинхронный протокол потокового чтения данных.
    """

    async def read(self: Self, size: int | None = READ_SIZE) -> bytes:
        """
        Читаем данные.
        """
        ...


StreamReadProtocol = StreamReadAsyncProtocol | StreamReadSyncProtocol


class StreamReaderProtocol(Protocol):
    """
    Протокол потокового чтения данных с контекстным менеджером.
    """

    async def read(self: Self, size: int = READ_SIZE) -> bytes:
        """
        Читаем данные.
        """
        ...

    def __aiter__(self: Self) -> AsyncIterator[bytes]:
        """
        Заходим в контекстный менеджер.
        """
        ...

    async def __anext__(self: Self) -> bytes:
        """
        Читаем следующую порцию данных.
        """
        ...


class AiofilesStreamReader:
    """
    Реализация потокового чтения данных для библиотеки `aiofiles`.
    """

    def __init__(self, reader: AsyncBufferedReader) -> None:
        self.reader = reader

    async def read(self: Self, size: int = READ_SIZE) -> bytes:
        """
        Читаем данные.
        """
        return await self.reader.read(size)

    def __aiter__(self: Self) -> AsyncIterator[bytes]:
        """
        Заходим в контекстный менеджер.
        """
        return self

    async def __anext__(self: Self) -> bytes:
        """
        Читаем следующую порцию данных.
        """
        chunk = await self.reader.read(READ_SIZE)
        if chunk:
            return chunk
        raise StopAsyncIteration()


class AiohttpStreamReader:
    """
    Реализация потокового чтения данных для библиотеки `aiohttp`.
    """

    def __init__(self, response: ClientResponse) -> None:
        self.response = response

    async def read(self: Self, size: int = READ_SIZE) -> bytes:
        """
        Читаем данные.
        """
        return await self.response.content.read(size)

    def __aiter__(self: Self) -> AsyncIterator[bytes]:
        """
        Заходим в контекстный менеджер.
        """
        return self

    async def __anext__(self: Self) -> bytes:
        """
        Читаем следующую порцию данных.
        """
        chunk = await self.response.content.read(READ_SIZE)
        if chunk:
            return chunk
        raise StopAsyncIteration()
