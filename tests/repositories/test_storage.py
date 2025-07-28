"""
Модуль, содержащий тесты репозиториев файлового хранилища.
"""

import io
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import cast

import pytest
from fast_clean.repositories.storage import StorageRepositoryProtocol, StreamReadProtocol

from .schemas import DirectorySchema, FileSchema
from .utils import walk_path, walk_str

FILES: list[FileSchema] = []
for i in range(1, 5):
    FILES.append(FileSchema(name=f'file{i}', content=f'file{i} content'.encode()))
FILES.append(FileSchema(name='large_file', content='large file content'.encode() * 1024))
DIRECTORY = DirectorySchema(
    name='',
    children=[
        FILES[0],
        DirectorySchema(name='directory1', children=[FILES[1], FILES[2]]),
        DirectorySchema(name='directory2', children=[FILES[3]]),
        DirectorySchema(name='directory3', children=[FILES[4]]),
    ],
)

NEW_FILE = 'new_file'
NEW_FILE_CONTENTS = ('ne file content 1', 'new_file content 2')


WALK_TYPE = Callable[[DirectorySchema], Iterator[tuple[str | Path, DirectorySchema | FileSchema]]]


@pytest.mark.parametrize(
    'storage_repository',
    [('local', DIRECTORY), ('s3', DIRECTORY)],
    indirect=True,
)
class TestStorageRepositories:
    """
    Тесты репозиториев файлового хранилища.
    """

    @staticmethod
    @pytest.mark.parametrize('walk', [walk_str, walk_path])
    async def test_exists(storage_repository: StorageRepositoryProtocol, walk: WALK_TYPE) -> None:
        """
        Тестируем метод `exists`.
        """
        async with storage_repository:
            for path, item in walk(DIRECTORY):
                if isinstance(item, FileSchema):
                    assert await storage_repository.exists(path)
            assert not await storage_repository.exists('unknown_file')

    @staticmethod
    @pytest.mark.parametrize('walk', [walk_str, walk_path])
    async def test_listdir(storage_repository: StorageRepositoryProtocol, walk: WALK_TYPE) -> None:
        """
        Тестируем метод `listdir`.
        """
        for path, item in walk(DIRECTORY):
            if isinstance(item, DirectorySchema):
                actual_paths: set[str] = set()
                for child in item.children:
                    child_path = str(Path(path) / child.name)
                    if isinstance(child, DirectorySchema):
                        child_path += '/'
                    actual_paths.add(child_path)
                async with storage_repository:
                    assert set(await storage_repository.listdir(path)) == actual_paths

    @staticmethod
    @pytest.mark.parametrize('walk', [walk_str, walk_path])
    async def test_is_file(storage_repository: StorageRepositoryProtocol, walk: WALK_TYPE) -> None:
        """
        Тестируем метод `is_file`.
        """
        async with storage_repository:
            for path, item in walk(DIRECTORY):
                if isinstance(item, FileSchema):
                    assert await storage_repository.is_file(path)
                else:
                    assert not await storage_repository.is_file(path)

    @staticmethod
    @pytest.mark.parametrize('walk', [walk_str, walk_path])
    async def test_is_dir(storage_repository: StorageRepositoryProtocol, walk: WALK_TYPE) -> None:
        """
        Тестируем метод `is_dir`.
        """
        async with storage_repository:
            for path, item in walk(DIRECTORY):
                if isinstance(item, DirectorySchema):
                    assert await storage_repository.is_dir(path)
                else:
                    assert not await storage_repository.is_dir(path)

    @staticmethod
    @pytest.mark.parametrize('walk', [walk_str, walk_path])
    async def test_read(storage_repository: StorageRepositoryProtocol, walk: WALK_TYPE) -> None:
        """
        Тестируем метод `read`.
        """
        async with storage_repository:
            for path, item in walk(DIRECTORY):
                if isinstance(item, FileSchema):
                    assert await storage_repository.read(path) == item.content

    @staticmethod
    @pytest.mark.parametrize('walk', [walk_str, walk_path])
    async def test_stream_read(storage_repository: StorageRepositoryProtocol, walk: WALK_TYPE) -> None:
        """
        Тестируем метод `stream_read`.
        """
        async with storage_repository:
            for path, item in walk(DIRECTORY):
                if isinstance(item, FileSchema):
                    actual_content = b''
                    async with storage_repository.stream_read(path) as reader:
                        async for chunk in reader:
                            actual_content += chunk
                    assert actual_content == item.content
                    async with storage_repository.stream_read(path) as reader:
                        assert await reader.read(5) == item.content[:5]

    @staticmethod
    @pytest.mark.parametrize('walk', [walk_str, walk_path])
    async def test_straming_read(storage_repository: StorageRepositoryProtocol, walk: WALK_TYPE) -> None:
        """
        Тестируем метод `straming_read`.
        """
        async with storage_repository:
            for path, item in walk(DIRECTORY):
                if isinstance(item, FileSchema):
                    actual_content = b''.join([chunk async for chunk in storage_repository.straming_read(path)])
                    assert actual_content == item.content

    @classmethod
    @pytest.mark.parametrize('new_file', [NEW_FILE, Path(NEW_FILE)])
    async def test_write(cls, storage_repository: StorageRepositoryProtocol, new_file: str | Path) -> None:
        """
        Тестируем метод `write`.
        """
        async with storage_repository:
            assert not await storage_repository.exists(new_file)
            for content in NEW_FILE_CONTENTS:
                await storage_repository.write(new_file, content)
                assert await storage_repository.read(new_file) == content.encode()
            await storage_repository.delete(new_file)

    @classmethod
    @pytest.mark.parametrize('new_file', [NEW_FILE, Path(NEW_FILE)])
    async def test_stream_write(cls, storage_repository: StorageRepositoryProtocol, new_file: str | Path) -> None:
        """
        Тестируем метод `stream_write`.
        """
        async with storage_repository:
            assert not await storage_repository.exists(new_file)
            for content in NEW_FILE_CONTENTS:
                encoded_content = content.encode()
                await storage_repository.stream_write(
                    new_file,
                    cast(StreamReadProtocol, io.BytesIO(encoded_content)),
                )
                assert await storage_repository.read(new_file) == encoded_content
            await storage_repository.delete(new_file)

    @staticmethod
    @pytest.mark.parametrize('walk', [walk_str, walk_path])
    async def test_delete(storage_repository: StorageRepositoryProtocol, walk: WALK_TYPE) -> None:
        """
        Тестируем метод `delete`.
        """
        async with storage_repository:
            for path, item in walk(DIRECTORY):
                if isinstance(item, FileSchema):
                    assert await storage_repository.exists(path)
                    await storage_repository.delete(path)
                    assert not await storage_repository.exists(path)
