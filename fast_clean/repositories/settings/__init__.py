"""
Package containing the settings repository.

Two implementations are provided:
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
    Settings repository protocol.
    """

    async def get(self: Self, schema_type: type[SettingsSchema], *, name: str | None = None) -> SettingsSchema:
        """
        Get settings.
        """
        ...


class SettingsRepositoryFactoryProtocol(Protocol):
    """
    Settings repository factory protocol.
    """

    async def make(self: Self, settings_source: SettingsSourceEnum) -> SettingsRepositoryProtocol:
        """
        Create a settings repository.
        """
        ...


class SettingsRepositoryFactoryImpl:
    """
    Settings repository factory implementation.
    """

    async def make(self: Self, settings_source: SettingsSourceEnum) -> SettingsRepositoryProtocol:
        """
        Create a settings repository.
        """
        match settings_source:
            case SettingsSourceEnum.ENV:
                return EnvSettingsRepository()
