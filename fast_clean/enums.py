"""
Module containing enums.
"""

from enum import StrEnum, auto
from typing import Self


class CascadeEnum(StrEnum):
    """
    Cascade behavior settings for SQLAlchemy.
    """

    CASCADE = 'CASCADE'

    SAVE_UPDATE = 'save-update'
    MERGE = 'merge'
    REFRESH_EXPIRE = 'refresh-expire'
    EXPUNGE = 'expunge'
    DELETE = 'delete'
    ALL = 'all'
    DELETE_ORPHAN = 'delete-orphan'

    ALL_DELETE_ORPHAN = 'all, delete-orphan'

    def __add__(self: Self, value: str) -> str:
        return f'{self}, {value}'

    def __radd__(self: Self, value: str) -> str:
        return f'{value}, {self}'


class ModelActionEnum(StrEnum):
    """
    Action on a model.
    """

    INSERT = auto()
    UPDATE = auto()
    UPSERT = auto()
    DELETE = auto()
