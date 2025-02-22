"""
Модуль для работы со строками.
"""

import base64
import string
from random import choice


def make_random_string(size: int) -> str:
    """
    Создаем случайную строку.
    """
    return ''.join(choice(string.ascii_letters + string.digits) for _ in range(size))


def encode_base64(raw_value: str) -> str:
    """
    Кодируем строку в base64.
    """
    return base64.b64encode(raw_value.encode()).decode()


def decode_base64(value: str) -> str:
    """
    Декодируем строку из base64.
    """
    return base64.b64decode(value).decode()
