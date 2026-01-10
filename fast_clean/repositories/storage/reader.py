"""
Module containing classes for streaming data reading.
"""

from collections.abc import AsyncIterator
from typing import Protocol, Self

from aiofiles.threadpool.binary import AsyncBufferedReader
from aiohttp import ClientResponse

READ_SIZE = 5 * 1024 * 1024


class StreamReadSyncProtocol(Protocol):
    """
    Synchronous streaming data reading protocol.
    """

    def read(self: Self, size: int | None = READ_SIZE) -> bytes:
        """
        Read data.
        """
        ...


class StreamReadAsyncProtocol(Protocol):
    """
    Asynchronous streaming data reading protocol.
    """

    async def read(self: Self, size: int | None = READ_SIZE) -> bytes:
        """
        Read data.
        """
        ...


class AsyncStreamReaderProtocol(Protocol):
    async def read(self: Self, size: int = -1) -> bytes:
        """
        Streaming file reading.
        """
        ...


StreamReadProtocol = StreamReadAsyncProtocol | StreamReadSyncProtocol


class StreamReaderProtocol(Protocol):
    """
    Streaming data reading protocol with a context manager.
    """

    async def read(self: Self, size: int = READ_SIZE) -> bytes:
        """
        Read data.
        """
        ...

    def __aiter__(self: Self) -> AsyncIterator[bytes]:
        """
        Enter the context manager.
        """
        ...

    async def __anext__(self: Self) -> bytes:
        """
        Read the next chunk of data.
        """
        ...


class AiofilesStreamReader:
    """
    Streaming data reading implementation for the `aiofiles` library.
    """

    def __init__(self, reader: AsyncBufferedReader) -> None:
        self.reader = reader

    async def read(self: Self, size: int = READ_SIZE) -> bytes:
        """
        Read data.
        """
        return await self.reader.read(size)

    def __aiter__(self: Self) -> AsyncIterator[bytes]:
        """
        Enter the context manager.
        """
        return self

    async def __anext__(self: Self) -> bytes:
        """
        Read the next chunk of data.
        """
        chunk = await self.reader.read(READ_SIZE)
        if chunk:
            return chunk
        raise StopAsyncIteration()


class AiohttpStreamReader:
    """
    Streaming data reading implementation for the `aiohttp` library.
    """

    def __init__(self, response: ClientResponse) -> None:
        self.response = response

    async def read(self: Self, size: int = READ_SIZE) -> bytes:
        """
        Read data.
        """
        return await self.response.content.read(size)

    def __aiter__(self: Self) -> AsyncIterator[bytes]:
        """
        Enter the context manager.
        """
        return self

    async def __anext__(self: Self) -> bytes:
        """
        Read the next chunk of data.
        """
        chunk = await self.response.content.read(READ_SIZE)
        if chunk:
            return chunk
        raise StopAsyncIteration()
