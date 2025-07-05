from enum import StrEnum, auto


class EnvironmentEnum(StrEnum):
    """
    Окружения
    """

    DEVELOPMENT = auto()
    PRODUCTION = auto()
