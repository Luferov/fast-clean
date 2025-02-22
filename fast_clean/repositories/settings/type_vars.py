"""
Модуль, содержащий переменные типов.
"""

from typing import TypeVar

from pydantic import BaseModel

SettingsSchema = TypeVar('SettingsSchema', bound=BaseModel)
