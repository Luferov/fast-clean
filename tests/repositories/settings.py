"""
Module containing test settings.
"""

from pydantic import BaseModel

from fast_clean.settings import BaseSettingsSchema


class UnknownSettingsSchema(BaseModel):
    """
    Test unknown settings schema.
    """

    value: str


class ServiceSettingsSchema(BaseModel):
    """
    Test service settings schema.
    """

    str_value: str
    int_value: int


class SettingsTest(BaseSettingsSchema):
    """
    Test settings.
    """

    service: ServiceSettingsSchema | None = None
