"""
Package containing the file storage repository.

Two implementations are provided:
- Local
- S3
"""

from collections.abc import AsyncIterator
from pathlib import Path
from typing import AsyncContextManager, Protocol, Self

from .enums import StorageTypeEnum
from .local import LocalStorageRepository
from .reader import AsyncStreamReaderProtocol as AsyncStreamReaderProtocol
from .reader import StreamReaderProtocol, StreamReadProtocol
from .s3 import S3StorageRepository
from .schemas import (
    LocalStorageParamsSchema,
    S3StorageParamsSchema,
    StorageParamsSchema,
)


class StorageRepositoryProtocol(Protocol):
    """
    File storage repository protocol.
    """

    async def __aenter__(self: Self) -> Self:
        """
        Enter the context manager.
        """
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the context manager.
        """
        ...

    async def exists(self: Self, path: str | Path) -> bool:
        """
        Check whether the file exists.
        """
        ...

    async def listdir(self: Self, path: str | Path) -> list[str]:
        """
        Get a list of files and directories in the specified directory.
        """
        ...

    async def is_file(self: Self, path: str | Path) -> bool:
        """
        Check whether a file exists at the path.
        """
        ...

    async def is_dir(self: Self, path: str | Path) -> bool:
        """
        Check whether a directory exists at the path.
        """
        ...

    async def read(self: Self, path: str | Path) -> bytes:
        """
        Read file contents.
        """
        ...

    def stream_read(self: Self, path: str | Path) -> AsyncContextManager[StreamReaderProtocol]:
        """
        Read file contents in streaming mode.
        """
        ...

    async def write(self: Self, path: str | Path, content: str | bytes) -> None:
        """
        Create a file or overwrite an existing one.
        """
        ...

    async def stream_write(
        self: Self,
        path: str | Path,
        stream: StreamReadProtocol,
    ) -> None:
        """
        Create a file or overwrite an existing one in streaming mode.
        """
        ...

    def straming_read(self: Self, path: str | Path) -> AsyncIterator[bytes]:
        """
        Return an asynchronous byte stream iterator.
        """
        ...

    async def delete(self: Self, path: str | Path) -> None:
        """
        Delete a file.
        """
        ...


class StorageRepositoryFactoryProtocol(Protocol):
    """
    File storage repository factory protocol.
    """

    async def make(self, storage_type: StorageTypeEnum, params: StorageParamsSchema) -> StorageRepositoryProtocol:
        """
        Create a file storage repository.
        """
        ...


class StorageRepositoryFactoryImpl:
    """
    File storage repository factory implementation.
    """

    async def make(self: Self, storage_type: StorageTypeEnum, params: StorageParamsSchema) -> StorageRepositoryProtocol:
        """
        Create a file storage repository.
        """
        if storage_type == StorageTypeEnum.S3 and isinstance(params, S3StorageParamsSchema):
            return S3StorageRepository(params)
        elif storage_type == StorageTypeEnum.LOCAL and isinstance(params, LocalStorageParamsSchema):
            return LocalStorageRepository(params)
        raise NotImplementedError()
