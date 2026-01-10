"""
Module for working with strings.
"""

import base64
import string
from random import choice


def make_random_string(size: int) -> str:
    """
    Create a random string.
    """
    return ''.join(choice(string.ascii_letters + string.digits) for _ in range(size))


def encode_base64(raw_value: str) -> str:
    """
    Encode a string to base64.
    """
    return base64.b64encode(raw_value.encode()).decode()


def decode_base64(value: str) -> str:
    """
    Decode a base64 string.
    """
    return base64.b64decode(value).decode()
