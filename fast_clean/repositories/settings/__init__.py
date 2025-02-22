"""
Пакет, содержащий репозиторий настроек.

Представлено 2 реализации:
- Env
- Prefect
"""

from typing import Protocol, Self

from .enums import SettingsSourceEnum
from .env import EnvSettingsRepository
from .exceptions import SettingsRepositoryError as SettingsRepositoryError
from .type_vars import SettingsSchema


class SettingsRepositoryProtocol(Protocol):
    """
    Протокол репозитория настроек.
    """

    async def get(self: Self, schema_type: type[SettingsSchema], *, name: str | None = None) -> SettingsSchema:
        """
        Получаем настройки.
        """
        ...


class SettingsRepositoryFactoryProtocol(Protocol):
    """
    Протокол фабрики репозиториев настроек.
    """

    async def make(self: Self, settings_source: SettingsSourceEnum) -> SettingsRepositoryProtocol:
        """
        Создаем репозиторий настроек.
        """
        ...


class SettingsRepositoryFactoryImpl:
    """
    Реализация фабрики репозиториев настроек.
    """

    async def make(self: Self, settings_source: SettingsSourceEnum) -> SettingsRepositoryProtocol:
        """
        Создаем репозиторий настроек.
        """
        match settings_source:
            case SettingsSourceEnum.ENV:
                return EnvSettingsRepository()
