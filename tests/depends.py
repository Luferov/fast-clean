"""
Module containing dependencies for tests.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Protocol, Self

from fastapi import Depends

# --- db ---


class Session:
    """
    Test session.
    """

    def __init__(self) -> None:
        self.in_transaction = False

    @asynccontextmanager
    async def begin(self: Self) -> AsyncIterator[Session]:
        """
        Start a session.
        """
        self.in_transaction = True
        yield self
        self.in_transaction = False


# --- repositories ---


class RepositoryUnknownProtocol(Protocol):
    """
    Test unknown repository protocol.
    """

    ...


class RepositoryAProtocol(Protocol):
    """
    Test repository A protocol.
    """

    ...


class RepositoryAImpl:
    """
    Test repository A implementation.
    """

    ...


class RepositoryBProtocol(Protocol):
    """
    Test repository B protocol.
    """

    ...


class RepositoryBImpl:
    """
    Test repository B implementation.
    """

    def __init__(self, session: Session) -> None:
        self.session = session


def get_repository_a() -> RepositoryAProtocol:
    """
    Get test repository A.
    """
    return RepositoryAImpl()


async def get_repository_b(
    session: Session | None = None,
) -> AsyncGenerator[RepositoryBProtocol, None]:
    """
    Get test repository B.
    """
    session = session or Session()
    async with session.begin() as session:
        yield RepositoryBImpl(session)


RepositoryA = Annotated[RepositoryAProtocol, Depends(get_repository_a, use_cache=False)]
RepositoryB = Annotated[RepositoryBProtocol, Depends(get_repository_b)]

# --- repositories ---


class ServiceAProtocol(Protocol):
    """
    Test service A protocol.
    """

    ...


class ServiceAImpl:
    """
    Test service A implementation.
    """

    def __init__(self, repository_a: RepositoryAProtocol, repository_b: RepositoryBProtocol) -> None:
        self.repository_a = repository_a
        self.repository_b = repository_b


class ServiceBProtocol(Protocol):
    """
    Test service B protocol.
    """

    ...


class ServiceBImpl:
    """
    Test service B implementation.
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
    Get test service A.
    """
    return ServiceAImpl(repository_a, repository_b)


def get_service_b(repository_a: RepositoryA, repository_b: RepositoryB, value: int) -> ServiceBProtocol:
    """
    Get test service B.
    """
    return ServiceBImpl(repository_a, repository_b, value)


ServiceA = Annotated[ServiceAProtocol, Depends(get_service_a)]
ServiceB = Annotated[ServiceBProtocol, Depends(get_service_b)]


class UseCaseAProtocol(Protocol):
    """
    Test use case A protocol.
    """

    ...


class UseCaseAImpl:
    """
    Test use case A implementation.
    """

    def __init__(self, service_a: ServiceAProtocol, service_b: ServiceBProtocol, value: str) -> None:
        self.service_a = service_a
        self.service_b = service_b
        self.value = value


def get_use_case_a(service_a: ServiceA, service_b: ServiceB, value: str) -> UseCaseAProtocol:
    """
    Get test use case A.
    """
    return UseCaseAImpl(service_a, service_b, value)


UseCaseA = Annotated[UseCaseAProtocol, Depends(get_use_case_a)]
