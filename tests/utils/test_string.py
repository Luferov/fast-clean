"""
Модуль, содержащий тесты работы со строками.
"""

import string

from fast_clean.utils.string import decode_base64, encode_base64, make_random_string


def test_make_random_string() -> None:
    """
    Тестируем функцию `make_random_string`.
    """
    random_string = make_random_string(10)
    assert len(random_string) == 10
    for char in random_string:
        assert char in string.ascii_letters + string.digits


def test_encode_base64() -> None:
    """
    Тестируем функцию `encode_base64`.
    """
    assert encode_base64('~string!') == 'fnN0cmluZyE='


def test_decode_base64() -> None:
    """
    Тестируем функцию `decode_base64`.
    """
    assert decode_base64('fnN0cmluZyE=') == '~string!'
