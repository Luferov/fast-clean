"""
Модуль, содержащий тестовые настройки.
"""

from fast_clean.settings import BaseSettingsSchema
from pydantic import BaseModel


class UnknownSettingsSchema(BaseModel):
    """
    Схема тестовых неизвестных настроек.
    """

    value: str


class ServiceSettingsSchema(BaseModel):
    """
    Схема тестовых настроек сервиса.
    """

    str_value: str
    int_value: int


class SettingsTest(BaseSettingsSchema):
    """
    Тестовые настройки.
    """

    service: ServiceSettingsSchema | None = None
