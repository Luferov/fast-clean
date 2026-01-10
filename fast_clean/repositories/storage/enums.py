"""
Module containing file storage enums.
"""

from enum import StrEnum, auto


class StorageTypeEnum(StrEnum):
    """
    Storage type.
    """

    S3 = auto()
    """
    S3 storage.
    """
    LOCAL = auto()
    """
    Local file storage.
    """
