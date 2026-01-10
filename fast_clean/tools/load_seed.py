"""
Module containing commands to load data from files.
"""

from typing import Annotated

import typer

from fast_clean.container import get_container
from fast_clean.services import SeedService
from fast_clean.utils import typer_async


@typer_async
async def load_seed(
    path: Annotated[str | None, typer.Argument(help='Path to the directory for loading data.')] = None,
) -> None:
    """
    Load data from files.
    """
    async with get_container() as container:
        seed_service = await container.get(SeedService)
        await seed_service.load_data(path)


def use_load_seed(app: typer.Typer) -> None:
    """
    Register commands to load data from files.
    """

    app.command()(load_seed)
