"""
Модуль, содержащий тестовые перечисления.
"""

from enum import StrEnum, auto


class CrudModelTypeEnum(StrEnum):
    """
    Тип модели для тестирования репозитория.
    """

    PARENT = auto()
    CHILD_A = auto()
    CHILD_B = auto()
