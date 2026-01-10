"""
Module containing string utility tests.
"""

import string

from fast_clean.utils.string import decode_base64, encode_base64, make_random_string


def test_make_random_string() -> None:
    """
    Test the `make_random_string` function.
    """
    random_string = make_random_string(10)
    assert len(random_string) == 10
    for char in random_string:
        assert char in string.ascii_letters + string.digits


def test_encode_base64() -> None:
    """
    Test the `encode_base64` function.
    """
    assert encode_base64('~string!') == 'fnN0cmluZyE='


def test_decode_base64() -> None:
    """
    Test the `decode_base64` function.
    """
    assert decode_base64('fnN0cmluZyE=') == '~string!'
