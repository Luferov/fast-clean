"""
Модель, содержащий тесты запуска тяжелых операций в ThreadPoolExecutor.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor

from fast_clean.utils.thread import run_in_threadpool


def add(a: int, b: int) -> int:
    """
    Тестовая функция сложения аргументов.
    """
    return a + b


async def test_run_in_threadpool() -> None:
    """
    Тестируем функцию `run_in_threadpool`.
    """
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor()
    loop.set_default_executor(executor)
    assert len(executor._threads) == 0
    assert await run_in_threadpool(add, 2, b=3) == 5
    assert len(executor._threads) == 1
