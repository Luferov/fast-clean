"""
Module containing type conversion tests.
"""

import pytest

from fast_clean.utils.type_converters import str_to_bool


def test_str_to_bool_true() -> None:
    """
    Test the `str_to_bool` function for strings that evaluate to true.
    """
    for true_value in ('yes', 'true', 't', 'y', '1'):
        assert str_to_bool(true_value)
        assert str_to_bool(true_value.upper())


def test_str_to_bool_false() -> None:
    """
    Test the `str_to_bool` function for strings that evaluate to false.
    """
    for false_value in ('no', 'false', 'f', 'n', '0'):
        assert not str_to_bool(false_value)
        assert not str_to_bool(false_value.upper())


def test_str_to_bool_unknown() -> None:
    """
    Test the `str_to_bool` function for unknown strings.
    """
    with pytest.raises(ValueError):
        str_to_bool('unknown')
