"""
Модуль, содержащий тесты вспомогательных функций для работы с Typer.
"""

from fast_clean.utils.typer import typer_async


def test_typer_async() -> None:
    """
    Тестируем декоратор `typer_async`.
    """

    @typer_async
    async def sum(a: int, b: int) -> int:
        return a + b

    assert sum(1, 2) == 3
