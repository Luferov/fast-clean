"""
Module containing tests for running heavy operations in ProcessPoolExecutor.
"""

import fast_clean.utils.process as process


def add(a: int, b: int) -> int:
    """
    Test function for adding arguments.
    """
    return a + b


async def test_run_in_processpool() -> None:
    """
    Test the `run_in_processpool` function.
    """
    assert process.process_pool is None
    assert await process.run_in_processpool(add, 2, b=3) == 5
    assert process.process_pool is not None
    assert len(process.process_pool._processes) == process.process_pool._max_workers
