"""
Module containing type variables.
"""

from typing import TypeVar

from pydantic import BaseModel

SettingsSchema = TypeVar('SettingsSchema', bound=BaseModel)
