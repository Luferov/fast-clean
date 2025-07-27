"""
Модуль, содержащий команды загрузки данных из файлов.
"""

from typing import Annotated

import typer

from fast_clean.container import get_container
from fast_clean.services import SeedService
from fast_clean.utils import typer_async


@typer_async
async def load_seed(
    path: Annotated[str | None, typer.Argument(help='Путь к директории для загрузки данных.')] = None,
) -> None:
    """
    Загружаем данные из файлов.
    """
    async with get_container() as container:
        seed_service = await container.get(SeedService)
        await seed_service.load_data(path)


def use_load_seed(app: typer.Typer) -> None:
    """
    Регистрируем команды загрузки данных из файлов.
    """

    app.command()(load_seed)
