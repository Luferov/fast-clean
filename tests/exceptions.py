"""
Модуль, содержащий исключения для тестов.
"""

from typing import Self

from fast_clean.exceptions import BusinessLogicException


class CustomTestError(BusinessLogicException):
    """
    Тестовая ошибка.
    """

    @property
    def msg(self: Self) -> str:
        return 'Тестовое сообщение'
