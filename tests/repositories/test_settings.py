"""
Модуль, содержащий тесты репозиториев настроек.
"""

import pytest
from fast_clean.repositories.settings import SettingsRepositoryError, SettingsRepositoryProtocol

from .settings import ServiceSettingsSchema, UnknownSettingsSchema

SERVICE = ServiceSettingsSchema(str_value='value', int_value=1)


@pytest.mark.parametrize('settings_repository', [('env', SERVICE)], indirect=True)
class TestSettingsRepositories:
    """
    Тесты репозиториев настроек.
    """

    @staticmethod
    async def test_get_without_name(settings_repository: SettingsRepositoryProtocol) -> None:
        """
        Тестируем метод `get` без имени.
        """
        with pytest.raises(SettingsRepositoryError):
            await settings_repository.get(UnknownSettingsSchema)
        assert await settings_repository.get(ServiceSettingsSchema) == SERVICE

    @staticmethod
    async def test_get_with_name(settings_repository: SettingsRepositoryProtocol) -> None:
        """
        Тестируем метод `get` с именем.
        """
        with pytest.raises(SettingsRepositoryError):
            await settings_repository.get(UnknownSettingsSchema, name='unknown')
        assert await settings_repository.get(ServiceSettingsSchema, name='service') == SERVICE
