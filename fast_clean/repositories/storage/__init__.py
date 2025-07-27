"""
Пакет, содержащий репозиторий файлового хранилища.

Представлено 2 реализации:
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
    Протокол репозитория файлового хранилища.
    """

    async def __aenter__(self: Self) -> Self:
        """
        Вход в контекст менеджера.
        """
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Выход из контекст менеджера.
        """
        ...

    async def exists(self: Self, path: str | Path) -> bool:
        """
        Проверяем существует ли файл.
        """
        ...

    async def listdir(self: Self, path: str | Path) -> list[str]:
        """
        Получаем список файлов и директорий в заданной директории.
        """
        ...

    async def is_file(self: Self, path: str | Path) -> bool:
        """
        Проверяем находится ли файл по пути.
        """
        ...

    async def is_dir(self: Self, path: str | Path) -> bool:
        """
        Проверяем находится ли директория по пути.
        """
        ...

    async def read(self: Self, path: str | Path) -> bytes:
        """
        Читаем содержимое файла.
        """
        ...

    def stream_read(self: Self, path: str | Path) -> AsyncContextManager[StreamReaderProtocol]:
        """
        Читаем содержимое файла в потоковом режиме.
        """
        ...

    async def write(self: Self, path: str | Path, content: str | bytes) -> None:
        """
        Создаем файл или переписываем существующий.
        """
        ...

    async def stream_write(
        self: Self,
        path: str | Path,
        stream: StreamReadProtocol,
    ) -> None:
        """
        Создаем файл или переписываем существующий в потоковом режиме.
        """
        ...

    def straming_read(self: Self, path: str | Path) -> AsyncIterator[bytes]:
        """
        Возвращаем асинхронные итератор потока байт.
        """
        ...

    async def delete(self: Self, path: str | Path) -> None:
        """
        Удаляем файл.
        """
        ...


class StorageRepositoryFactoryProtocol(Protocol):
    """
    Протокол фабрики репозиториев файлового хранилища.
    """

    async def make(self, storage_type: StorageTypeEnum, params: StorageParamsSchema) -> StorageRepositoryProtocol:
        """
        Создаем репозиторий файлового хранилища.
        """
        ...


class StorageRepositoryFactoryImpl:
    """
    Реализация фабрики репозиториев файлового хранилища.
    """

    async def make(self: Self, storage_type: StorageTypeEnum, params: StorageParamsSchema) -> StorageRepositoryProtocol:
        """
        Создаем репозиторий файлового хранилища.
        """
        if storage_type == StorageTypeEnum.S3 and isinstance(params, S3StorageParamsSchema):
            return S3StorageRepository(params)
        elif storage_type == StorageTypeEnum.LOCAL and isinstance(params, LocalStorageParamsSchema):
            return LocalStorageRepository(params)
        raise NotImplementedError()
