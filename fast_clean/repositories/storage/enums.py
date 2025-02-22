"""
Модуль, содержащий перечисления файлового хранилища.
"""

from enum import StrEnum, auto


class StorageTypeEnum(StrEnum):
    """
    Тип хранилища.
    """

    S3 = auto()
    """
    Хранилище S3.
    """
    LOCAL = auto()
    """
    Локальное файловое хранилище.
    """
