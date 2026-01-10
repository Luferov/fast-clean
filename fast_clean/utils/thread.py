"""
Model for running heavy operations in ThreadPoolExecutor.
"""

import asyncio
from functools import partial
from typing import Callable, TypeVar

from typing_extensions import ParamSpec

R = TypeVar('R')
P = ParamSpec('P')


async def run_in_threadpool(fn: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
    """
    Run a function in a separate thread.
    """
    kwargs_fn = partial(fn, *args, **kwargs)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, kwargs_fn)
