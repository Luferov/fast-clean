"""
Module containing settings repository exceptions.
"""


class SettingsRepositoryError(Exception):
    """
    Settings repository error.
    """

    def __init__(self, message: str, *args: object) -> None:
        super().__init__(*args)
        self.message = message
