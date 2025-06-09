"""
Модуль, содержащий контейнер зависимостей.
"""

import importlib
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI


class ContainerManager:
    """
    Менеджер для управления контейнером зависимостей.
    """

    DEPENDS_MODULE = 'depends'

    container: AsyncContainer | None = None

    @classmethod
    def init(cls, module_names: set[str] | None = None) -> AsyncContainer:
        """
        Инициализируем контейнер зависимостей.
        """
        if cls.container is None:
            cls.container = cls.create(module_names)
        return cls.container

    @classmethod
    def init_for_fastapi(cls, app: FastAPI, module_names: set[str] | None = None) -> AsyncContainer:
        """
        Инициализируем контейнер зависимостей для приложения FastAPI.
        """
        container = cls.init(module_names)
        setup_dishka(container=container, app=app)
        return container

    @classmethod
    async def close(cls) -> None:
        """
        Закрываем контейнер зависимостей.
        """
        if cls.container is None:
            return
        await cls.container.close()
        cls.container = None

    @classmethod
    def create(cls, module_names: set[str] | None = None) -> AsyncContainer:
        """
        Создаем контейнер зависимостей.
        """
        module_names = module_names or set()
        module_names.update(cls.get_default_module_names())
        return make_async_container(FastapiProvider(), *cls.get_providers(module_names))

    @classmethod
    def get_default_module_names(cls) -> set[str]:
        """
        Получаем список модулей с зависимостями по умолчанию.
        """
        cwd = Path(os.getcwd())
        virtual_env_paths = {path.parent for path in cwd.rglob('pyvenv.cfg')}
        module_names: set[str] = set()
        for path in cwd.rglob(f'{cls.DEPENDS_MODULE}.py'):
            if not any(path.is_relative_to(venv) for venv in virtual_env_paths):
                module_names.add('.'.join(str(path.relative_to(cwd).with_suffix('')).split('/')))
        module_names.add(f'fast_clean.{cls.DEPENDS_MODULE}')
        return module_names

    @staticmethod
    def get_providers(module_names: set[str]) -> list[Provider]:
        """
        Получаем провайдеры зависимостей.
        """
        providers: list[Provider] = []
        for module_name in module_names:
            module = sys.modules[module_name] if module_name in sys.modules else importlib.import_module(module_name)
            for obj in module.__dict__.values():
                if isinstance(obj, Provider):
                    providers.append(obj)
        return providers


@asynccontextmanager
async def get_container() -> AsyncIterator[AsyncContainer]:
    """
    Получаем контейнер зависимостей.
    """
    container = ContainerManager.container
    if container is None:
        container = ContainerManager.init()
    async with container() as nested_container:
        yield nested_container
