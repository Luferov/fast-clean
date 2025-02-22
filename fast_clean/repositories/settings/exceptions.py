"""
Модуль, содержащий исключения репозитория настроек.
"""


class SettingsRepositoryError(Exception):
    """
    Ошибка репозитория настроек.
    """

    def __init__(self, message: str, *args: object) -> None:
        super().__init__(*args)
        self.message = message
