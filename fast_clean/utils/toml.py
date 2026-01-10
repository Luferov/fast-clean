import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel

__all__ = (
    'use_toml_info',
    'ProjectInfo',
)


class ProjectInfo(BaseModel):
    """
    Schema for retrieving project information.
    """

    name: str
    version: str
    description: str | None = None


def use_toml(dir: Path) -> dict[str, Any]:
    with open(Path(dir) / 'pyproject.toml', 'rb') as f:
        return tomllib.load(f)


@lru_cache(maxsize=1)
def use_toml_info(dir: Path) -> ProjectInfo:
    """
    Get the application version from pyproject.toml.
    """
    return ProjectInfo.model_validate(use_toml(dir)['project'])
