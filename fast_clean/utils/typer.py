"""
Модуль, содержащий вспомогательные функции для работы с Typer.
"""

import asyncio
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, ParamSpec, TypeVar

Param = ParamSpec('Param')
RetType = TypeVar('RetType')


def typer_async(func: Callable[Param, Coroutine[Any, Any, RetType]]) -> Callable[Param, RetType]:
    """
    Декоратор для асинхронного запуска Typer.
    """

    @wraps(func)
    def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
        return asyncio.run(func(*args, **kwargs))

    return wrapper
