"""
Модуль, содержащий тесты преобразования типов.
"""

import pytest
from fast_clean.utils.type_converters import str_to_bool


def test_str_to_bool_true() -> None:
    """
    Тестируем функцию `str_to_bool` для строк, преобразующихся в истину.
    """
    for true_value in ('yes', 'true', 't', 'y', '1'):
        assert str_to_bool(true_value)
        assert str_to_bool(true_value.upper())


def test_str_to_bool_false() -> None:
    """
    Тестируем функцию `str_to_bool` для строк, преобразующихся в ложь.
    """
    for false_value in ('no', 'false', 'f', 'n', '0'):
        assert not str_to_bool(false_value)
        assert not str_to_bool(false_value.upper())


def test_str_to_bool_unknown() -> None:
    """
    Тестируем функцию `str_to_bool` для неизвестных строк.
    """
    with pytest.raises(ValueError):
        str_to_bool('unknown')
