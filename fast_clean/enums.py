"""
Модуль, содержащий перечисления.
"""

from enum import StrEnum, auto
from typing import Self


class CascadeEnum(StrEnum):
    """
    Настройки каскадного поведения для SQLAlchemy.
    """

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
    Действие с моделью.
    """

    INSERT = auto()
    UPDATE = auto()
    UPSERT = auto()
    DELETE = auto()
