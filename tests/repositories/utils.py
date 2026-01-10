"""
Module containing helper functions for tests.
"""

from collections.abc import Iterator
from pathlib import Path

from .schemas import DirectorySchema, FileSchema


def walk_path(
    directory: DirectorySchema, parent_path: Path | None = None
) -> Iterator[tuple[Path, DirectorySchema | FileSchema]]:
    """
    Traverse the directory, returning paths as Path.
    """
    parent_path = parent_path or Path('')
    directory_path = parent_path / directory.name
    yield directory_path, directory
    for child in directory.children:
        if isinstance(child, DirectorySchema):
            yield from walk_path(child, directory_path)
        else:
            yield directory_path / child.name, child


def walk_str(
    directory: DirectorySchema, parent_path: Path | None = None
) -> Iterator[tuple[str, DirectorySchema | FileSchema]]:
    """
    Traverse the directory, returning paths as str.
    """
    for path, item in walk_path(directory, parent_path):
        yield '' if path == Path('') else str(path), item
