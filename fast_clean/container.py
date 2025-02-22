"""
Модуль, содержащий контейнер зависимостей.
"""

from __future__ import annotations

import importlib
import inspect
import os
import sys
from collections.abc import Callable
from contextlib import AsyncExitStack
from pathlib import Path
from types import TracebackType
from typing import (
    Annotated,
    Any,
    Protocol,
    Self,
    get_args,
    get_origin,
    get_type_hints,
)

from fastapi.dependencies.utils import (
    is_async_gen_callable,
    is_coroutine_callable,
    is_gen_callable,
    solve_generator,
)
from fastapi.params import Depends
from starlette.concurrency import run_in_threadpool
from stringcase import pascalcase

from .exceptions import ContainerError


class ContainerProtocol(Protocol):
    """
    Протокол контейнера зависимостей.
    """

    def __call__(self: Self, extra: dict[tuple[str, Any], Any] | None = None) -> ContainerProtocol:
        """
        Получаем новый контейнер.
        """
        ...

    async def __aenter__(self: Self) -> ContainerProtocol:
        """
        Открываем асинхронный контекстный менеджер для управления стеком контекстных менеджеров.
        """
        ...

    async def __aexit__(
        self: Self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: TracebackType | None = None,
    ) -> None:
        """
        Закрываем асинхронный контекстный менеджер для управления стеком контекстных менеджеров.
        """
        ...

    async def get_by_type(self: Self, dependency_type: Any, *, extra: dict[tuple[str, Any], Any] | None = None) -> Any:
        """
        Получаем зависимость по типу.
        """
        ...

    async def get_by_name(self: Self, name: str, *, extra: dict[tuple[str, Any], Any] | None = None) -> Any:
        """
        Получаем зависимость по имени.
        """
        ...


class ContainerImpl:
    """
    Реализация контейнера зависимостей.
    """

    DEPENDS_MODULE = 'depends'

    dependencies_name_mapping: dict[str, Annotated[Any, Depends]] | None = None
    dependencies_type_mapping: dict[type, Annotated[Any, Depends]] | None = None

    def __init__(self, extra: dict[tuple[str, Any], Any] | None = None) -> None:
        self.extra = extra
        self.instances: dict[type, Any] = {}
        self.async_exit_stack: AsyncExitStack | None = None

    def __call__(self: Self, extra: dict[tuple[str, Any], Any] | None = None) -> ContainerProtocol:
        """
        Получаем новый контейнер.
        """
        return ContainerImpl(extra)

    async def __aenter__(self: Self) -> ContainerProtocol:
        """
        Открываем асинхронный контекстный менеджер для управления стеком контекстных менеджеров.
        """
        self.async_exit_stack = AsyncExitStack()
        return self

    async def __aexit__(
        self: Self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: TracebackType | None = None,
    ) -> None:
        """
        Закрываем асинхронный контекстный менеджер для управления стеком контекстных менеджеров.
        """
        assert self.async_exit_stack is not None
        await self.async_exit_stack.__aexit__(exc_type, exc_val, exc_tb)

    async def get_by_type(self: Self, dependency_type: Any, *, extra: dict[tuple[str, Any], Any] | None = None) -> Any:
        """
        Получаем зависимость по типу.
        """
        extra = extra or self.extra or {}
        assert self.dependencies_type_mapping is not None
        if dependency_type not in self.dependencies_type_mapping:
            raise ContainerError(f'Dependency {dependency_type} not found')
        return await self.resolve_dependency(self.dependencies_type_mapping[dependency_type], extra)

    async def get_by_name(self: Self, name: str, *, extra: dict[tuple[str, Any], Any] | None = None) -> Any:
        """
        Получаем зависимость по имени.
        """
        extra = extra or self.extra or {}
        assert self.dependencies_name_mapping is not None
        name = pascalcase(name)
        if name not in self.dependencies_name_mapping:
            raise ContainerError(f'Dependency {name} not found')
        return await self.resolve_dependency(self.dependencies_name_mapping[name], extra)

    async def resolve_dependency(self: Self, annotated_type: type, extra: dict[tuple[str, Any], Any]) -> Any:
        """
        Разрешаем зависимость.
        """
        dependency_type: type
        depends: Depends
        dependency_type, depends = get_args(annotated_type)
        if dependency_type in self.instances:
            return self.instances[dependency_type]
        call = depends.dependency
        assert call is not None
        resolved_params = await self.resolve_params(call, extra)
        if is_gen_callable(call) or is_async_gen_callable(call):
            if self.async_exit_stack is None:
                raise ContainerError('Generator requires `async_exit_stack`')
            resolved = await solve_generator(call=call, stack=self.async_exit_stack, sub_values=resolved_params)
        elif is_coroutine_callable(call):
            resolved = await call(**resolved_params)
        else:
            resolved = await run_in_threadpool(call, **resolved_params)
        if depends.use_cache:
            self.instances[dependency_type] = resolved
        return resolved

    async def resolve_params(self: Self, call: Callable[..., Any], extra: dict[tuple[str, Any], Any]) -> dict[str, Any]:
        """
        Разрешаем параметры зависимости.
        """
        signature = inspect.signature(call)
        resolved_params: dict[str, Any] = {}
        type_hints = get_type_hints(call, include_extras=True)
        for param_name, param in signature.parameters.items():
            annotation = type_hints[param_name]
            args = get_args(annotation)
            if (param_name, annotation) in extra:
                extra_value = extra[param_name, annotation]
                resolved_params[param_name] = extra_value() if callable(extra_value) else extra_value
            elif get_origin(annotation) is Annotated and len(args) == 2 and isinstance(args[1], Depends):
                resolved_params[param_name] = await self.resolve_dependency(annotation, extra)
            elif param.default is not inspect.Parameter.empty:
                resolved_params[param_name] = param.default
            else:
                raise ContainerError(f'Can not resolve dependency {param_name}: {annotation}')
        return resolved_params

    @classmethod
    def init(cls, module_names: set[str] | None = None) -> None:
        """
        Инициализируем контейнер.
        """
        if cls.dependencies_name_mapping is None:
            module_names = module_names or cls.get_default_module_names()
            cls.dependencies_name_mapping = cls.get_dependencies_name_mapping(module_names)
        if cls.dependencies_type_mapping is None:
            cls.dependencies_type_mapping = cls.get_dependencies_type_mapping()

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
    def get_dependencies_name_mapping(
        module_names: set[str],
    ) -> dict[str, Annotated[Any, Depends]]:
        """
        Получаем маппинг имен на зависимости.
        """
        name_mapping: dict[str, Annotated[Any, Depends]] = {}
        for module_name in module_names:
            module = sys.modules[module_name] if module_name in sys.modules else importlib.import_module(module_name)
            for name, obj in module.__dict__.items():
                args = get_args(obj)
                if get_origin(obj) is Annotated and len(args) == 2 and isinstance(args[1], Depends):
                    name_mapping[name] = obj
        return name_mapping

    @classmethod
    def get_dependencies_type_mapping(cls) -> dict[type, Annotated[Any, Depends]]:
        """
        Получаем маппинг типов на зависимости.
        """
        assert cls.dependencies_name_mapping is not None
        type_mapping: dict[type, Annotated[Any, Depends]] = {}
        for dependency in cls.dependencies_name_mapping.values():
            type_mapping[get_args(dependency)[0]] = dependency
        return type_mapping
