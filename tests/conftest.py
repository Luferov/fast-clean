"""
Модуль, содержащий фикстуры для тестов.
"""

import asyncio
from asyncio import AbstractEventLoop
from collections.abc import Iterator
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fast_clean.container import ContainerImpl, ContainerProtocol
from fast_clean.db import SessionManagerImpl, make_async_session_factory

from .settings import SettingsSchema


@pytest.fixture(scope='session', autouse=True)
def env() -> None:
    """
    Загружаем переменные окружения из файла при наличии и перезагружаем настройки Prefect.
    """
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)


@pytest.fixture(scope='session')
def event_loop() -> Iterator[AbstractEventLoop]:
    """
    Исправляет ошибку `RuntimeError: Event loop is closed`, возникающую из-за aioredis.
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
    Получаем настройки.
    """
    return SettingsSchema()  # type: ignore


@pytest.fixture
async def session_manager(settings: SettingsSchema) -> SessionManagerImpl:
    """
    Получаем менеджер сессий.
    """
    async with make_async_session_factory(settings.db.dsn)() as session:
        return SessionManagerImpl(session)


@pytest.fixture
async def container() -> ContainerProtocol:
    """
    Получаем контейнер зависимостей.
    """
    container = ContainerImpl()
    module_names = container.get_default_module_names()
    module_names.add('tests.depends')
    container.init(module_names)
    return container
