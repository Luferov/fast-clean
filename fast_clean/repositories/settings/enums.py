"""
Модуль, содержащий перечисления репозитория настроек.
"""

from enum import StrEnum, auto


class SettingsSourceEnum(StrEnum):
    """
    Источник настроек.
    """

    ENV = auto()
    """
    Настройки, получаемые из переменных окружения.
    """
