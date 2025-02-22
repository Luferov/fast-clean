"""
Модуль, содержащий зависимости для тестов.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Protocol, Self

from fastapi import Depends

# --- db ---


class Session:
    """
    Тестовая сессия.
    """

    def __init__(self) -> None:
        self.in_transaction = False

    @asynccontextmanager
    async def begin(self: Self) -> AsyncIterator[Session]:
        """
        Запускаем сессию.
        """
        self.in_transaction = True
        yield self
        self.in_transaction = False


# --- repositories ---


class RepositoryUnknownProtocol(Protocol):
    """
    Протокол тестового неизвестного репозитория.
    """

    ...


class RepositoryAProtocol(Protocol):
    """
    Протокол тестового репозитория A.
    """

    ...


class RepositoryAImpl:
    """
    Реализация тестового репозитория A.
    """

    ...


class RepositoryBProtocol(Protocol):
    """
    Протокол тестового репозитория B.
    """

    ...


class RepositoryBImpl:
    """
    Реализация тестового репозитория B.
    """

    def __init__(self, session: Session) -> None:
        self.session = session


def get_repository_a() -> RepositoryAProtocol:
    """
    Получаем тестовый репозиторий A.
    """
    return RepositoryAImpl()


async def get_repository_b(
    session: Session | None = None,
) -> AsyncGenerator[RepositoryBProtocol, None]:
    """
    Получаем тестовый репозиторий B.
    """
    session = session or Session()
    async with session.begin() as session:
        yield RepositoryBImpl(session)


RepositoryA = Annotated[RepositoryAProtocol, Depends(get_repository_a, use_cache=False)]
RepositoryB = Annotated[RepositoryBProtocol, Depends(get_repository_b)]

# --- repositories ---


class ServiceAProtocol(Protocol):
    """
    Протокол тестового сервиса A.
    """

    ...


class ServiceAImpl:
    """
    Реализация тестового сервиса A.
    """

    def __init__(self, repository_a: RepositoryAProtocol, repository_b: RepositoryBProtocol) -> None:
        self.repository_a = repository_a
        self.repository_b = repository_b


class ServiceBProtocol(Protocol):
    """
    Протокол тестового сервиса B.
    """

    ...


class ServiceBImpl:
    """
    Реализация тестового сервиса B.
    """

    def __init__(
        self,
        repository_a: RepositoryAProtocol,
        repository_b: RepositoryBProtocol,
        value: int,
    ) -> None:
        self.repository_a = repository_a
        self.repository_b = repository_b
        self.value = value


def get_service_a(repository_a: RepositoryA, repository_b: RepositoryB) -> ServiceAProtocol:
    """
    Получаем тестовый сервис A.
    """
    return ServiceAImpl(repository_a, repository_b)


def get_service_b(repository_a: RepositoryA, repository_b: RepositoryB, value: int) -> ServiceBProtocol:
    """
    Получаем тестовый сервис B.
    """
    return ServiceBImpl(repository_a, repository_b, value)


ServiceA = Annotated[ServiceAProtocol, Depends(get_service_a)]
ServiceB = Annotated[ServiceBProtocol, Depends(get_service_b)]


class UseCaseAProtocol(Protocol):
    """
    Протокол тестового варианта использования A.
    """

    ...


class UseCaseAImpl:
    """
    Реализация тестового варианта использования A.
    """

    def __init__(self, service_a: ServiceAProtocol, service_b: ServiceBProtocol, value: str) -> None:
        self.service_a = service_a
        self.service_b = service_b
        self.value = value


def get_use_case_a(service_a: ServiceA, service_b: ServiceB, value: str) -> UseCaseAProtocol:
    """
    Получаем тестовый вариант использования A.
    """
    return UseCaseAImpl(service_a, service_b, value)


UseCaseA = Annotated[UseCaseAProtocol, Depends(get_use_case_a)]
