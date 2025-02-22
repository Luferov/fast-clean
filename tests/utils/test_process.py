"""
Модуль, содержащий тесты запуска тяжелых операций в ProcessPoolExecutor.
"""

import fast_clean.utils.process as process


def add(a: int, b: int) -> int:
    """
    Тестовая функция сложения аргументов.
    """
    return a + b


async def test_run_in_processpool() -> None:
    """
    Тестируем функцию `run_in_processpool`.
    """
    assert process.process_pool is None
    assert await process.run_in_processpool(add, 2, b=3) == 5
    assert process.process_pool is not None
    assert len(process.process_pool._processes) == process.process_pool._max_workers
