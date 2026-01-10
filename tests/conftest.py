"""
Module containing fixtures for tests.
"""

import asyncio
from asyncio import AbstractEventLoop
from collections.abc import Iterator
from pathlib import Path
from typing import AsyncIterator

import pytest
from dishka import AsyncContainer
from dotenv import load_dotenv

from fast_clean.container import ContainerManager
from fast_clean.db import SessionManagerImpl, make_async_session_factory

from .settings import SettingsSchema


@pytest.fixture(scope='session', autouse=True)
def env() -> None:
    """
    Load environment variables from a file if present and reload Prefect settings.
    """
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)


@pytest.fixture(scope='session')
def event_loop() -> Iterator[AbstractEventLoop]:
    """
    Fixes the `RuntimeError: Event loop is closed` error caused by aioredis.
    https://stackoverflow.com/questions/61022713/pytest-asyncio-has-a-closed-event-loop-but-only-when-running-all-tests
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def settings() -> SettingsSchema:
    """
    Get settings.
    """
    return SettingsSchema()  # type: ignore


@pytest.fixture
async def session_manager(settings: SettingsSchema) -> SessionManagerImpl:
    """
    Get the session manager.
    """
    async with make_async_session_factory(settings.db.dsn)() as session:
        return SessionManagerImpl(session)


@pytest.fixture
async def container() -> AsyncIterator[AsyncContainer]:
    """
    Get the dependency container.
    """
    container = ContainerManager.create()
    async with container() as nested_container:
        yield nested_container


@pytest.fixture(scope='session', autouse=True)
def anyio_backend() -> str:
    return 'asyncio'
