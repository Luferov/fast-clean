"""
Module containing settings repository enums.
"""

from enum import StrEnum, auto


class SettingsSourceEnum(StrEnum):
    """
    Settings source.
    """

    ENV = auto()
    """
    Settings obtained from environment variables.
    """
