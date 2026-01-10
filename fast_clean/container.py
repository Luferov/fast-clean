"""
Module containing the dependency container.
"""

from collections.abc import AsyncIterator, Iterable
from contextlib import asynccontextmanager

from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.fastapi import FastapiProvider
from dishka.integrations.fastapi import setup_dishka as fastapi_setup_dishka
from dishka.integrations.faststream import FastStreamProvider
from dishka.integrations.faststream import setup_dishka as faststream_setup_dishka
from dishka.integrations.taskiq import TaskiqProvider
from dishka.integrations.taskiq import setup_dishka as taskiq_setup_dishka
from fastapi import FastAPI
from faststream import FastStream
from faststream.asgi import AsgiFastStream
from taskiq import AsyncBroker

from .utils.modules import get_instances, get_modules_by_names


class ContainerManager:
    """
    Manager for controlling the dependency container.
    """

    DEPENDS_MODULE = 'depends'

    container: AsyncContainer | None = None

    @classmethod
    def init(
        cls,
        module_names: set[str] | None = None,
        application_providers: Iterable[Provider] | None = None,
    ) -> AsyncContainer:
        """
        Initialize the dependency container.
        """
        if cls.container is None:
            cls.container = cls.create(application_providers=application_providers, module_names=module_names)
        return cls.container

    @classmethod
    def init_for_fastapi(
        cls,
        app: FastAPI,
        module_names: set[str] | None = None,
        additional_providers: Iterable[Provider] | None = None,
    ) -> AsyncContainer:
        application_providers: list[Provider] = [FastapiProvider()]
        if additional_providers is not None:
            application_providers.extend(additional_providers)
        container = cls.init(application_providers=application_providers, module_names=module_names)
        fastapi_setup_dishka(container, app)
        return container

    @classmethod
    def init_for_faststream(
        cls,
        app: FastStream | AsgiFastStream,
        module_names: set[str] | None = None,
        additional_providers: Iterable[Provider] | None = None,
    ) -> AsyncContainer:
        application_providers: list[Provider] = [FastStreamProvider()]
        if additional_providers is not None:
            application_providers.extend(additional_providers)
        container = cls.init(application_providers=application_providers, module_names=module_names)
        faststream_setup_dishka(container, app)  # type: ignore[arg-type]
        return container

    @classmethod
    def init_for_taskiq(
        cls,
        app: AsyncBroker,
        module_names: set[str] | None = None,
        additional_providers: Iterable[Provider] | None = None,
    ) -> AsyncContainer:
        application_providers: list[Provider] = [TaskiqProvider()]
        if additional_providers is not None:
            application_providers.extend(additional_providers)
        container = cls.init(application_providers=application_providers, module_names=module_names)
        taskiq_setup_dishka(container, app)
        return container

    @classmethod
    async def close(cls) -> None:
        """
        Close the dependency container.
        """
        if cls.container is None:
            return
        await cls.container.close()
        cls.container = None

    @classmethod
    def create(
        cls, module_names: set[str] | None = None, application_providers: Iterable[Provider] | None = None
    ) -> AsyncContainer:
        """
        Create the dependency container.
        """
        module_names = module_names or set()
        module_names.update(cls.get_default_module_names())
        providers = cls.get_providers(module_names)

        if application_providers is None:
            application_providers = [FastapiProvider()]

        return make_async_container(*providers, *application_providers)

    @classmethod
    def get_default_module_names(cls) -> set[str]:
        """
        Get a list of modules with default dependencies.
        """
        return get_modules_by_names(cls.DEPENDS_MODULE)

    @staticmethod
    def get_providers(module_names: set[str]) -> list[Provider]:
        """
        Get dependency providers.
        """
        return get_instances(module_names, Provider)


@asynccontextmanager
async def get_container(application_providers: Iterable[Provider] | None = None) -> AsyncIterator[AsyncContainer]:
    """
    Get the dependency container.
    """
    container = ContainerManager.container
    if container is None:
        container = ContainerManager.init(application_providers=application_providers)
    async with container() as nested_container:
        yield nested_container
