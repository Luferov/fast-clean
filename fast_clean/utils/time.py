"""
Module for working with date and time.
"""

import datetime as dt


def ts_now(*, tz=dt.timezone.utc) -> float:
    """
    Return the current GMT timestamp.

    :return: Value in seconds
    """
    return dt.datetime.now(tz).timestamp()
