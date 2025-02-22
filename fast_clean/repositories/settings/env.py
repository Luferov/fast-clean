"""
Модуль, содержащий репозиторий настроек, получаемых из переменных окружения.
"""

from typing import Self

from fast_clean.settings import BaseSettingsSchema, CoreSettingsSchema

from .exceptions import SettingsRepositoryError
from .type_vars import SettingsSchema


class EnvSettingsRepository:
    """
    Репозиторий настроек, получаемых из переменных окружения.
    """

    SETTINGS_MODULE = 'settings'

    settings: list[BaseSettingsSchema] | None = None

    async def get(self: Self, schema_type: type[SettingsSchema], *, name: str | None = None) -> SettingsSchema:
        """
        Получаем настройки из переменных окружения.
        """
        if self.settings is None:
            self.settings = [st() for st in BaseSettingsSchema.descendant_types if st is not CoreSettingsSchema]
        if name is not None:
            return self.get_by_name(schema_type, name)
        return self.get_by_type(schema_type)

    def get_by_name(self: Self, schema_type: type[SettingsSchema], name: str) -> SettingsSchema:
        """
        Получаем настройки по имени.
        """
        assert self.settings
        for settings in self.settings:
            value = getattr(settings, name, None)
            if value is not None and isinstance(value, schema_type):
                return value
        raise SettingsRepositoryError(f'Settings with name {name} not found')

    def get_by_type(self: Self, schema_type: type[SettingsSchema]) -> SettingsSchema:
        """
        Получаем настройки по типу.
        """
        assert self.settings
        for settings in self.settings:
            if isinstance(settings, schema_type):
                return settings
            for key in settings.__dict__.keys():
                value = getattr(settings, key, None)
                if isinstance(value, schema_type):
                    return value
        raise SettingsRepositoryError(f'Settings with type {schema_type} not found')
