"""
Module containing exceptions for tests.
"""

from typing import Self

from fast_clean.exceptions import BusinessLogicException


class CustomTestError(BusinessLogicException):
    """
    Test error.
    """

    @property
    def message(self: Self) -> str:
        return 'Test message'
