"""
Модуль для работы с датой и временем.
"""

import datetime as dt


def ts_now() -> float:
    """
    Возвращает текущий timestamp по GMT.

    :return: Значение в секундах
    """
    return dt.datetime.now(dt.timezone.utc).timestamp()
