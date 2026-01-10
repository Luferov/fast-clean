"""
Module containing test enums.
"""

from enum import StrEnum, auto


class CrudModelTypeEnum(StrEnum):
    """
    Model type for repository testing.
    """

    PARENT = auto()
    CHILD_A = auto()
    CHILD_B = auto()
