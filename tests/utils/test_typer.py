"""
Module containing tests for Typer helper functions.
"""

from fast_clean.utils.typer import typer_async


def test_typer_async() -> None:
    """
    Test the `typer_async` decorator.
    """

    @typer_async
    async def sum(a: int, b: int) -> int:
        return a + b

    assert sum(1, 2) == 3
