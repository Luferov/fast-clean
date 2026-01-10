"""
Model containing tests for running heavy operations in ThreadPoolExecutor.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor

from fast_clean.utils.thread import run_in_threadpool


def add(a: int, b: int) -> int:
    """
    Test function for adding arguments.
    """
    return a + b


async def test_run_in_threadpool() -> None:
    """
    Test the `run_in_threadpool` function.
    """
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor()
    loop.set_default_executor(executor)
    assert len(executor._threads) == 0
    assert await run_in_threadpool(add, 2, b=3) == 5
    assert len(executor._threads) == 1
