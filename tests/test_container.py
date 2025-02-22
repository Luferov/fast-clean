"""
Модуль, содержащий тесты контейнера зависимостей.
"""

from typing import cast

import pytest
from fast_clean.container import ContainerImpl, ContainerProtocol
from fast_clean.exceptions import ContainerError

from .depends import (
    RepositoryAImpl,
    RepositoryAProtocol,
    RepositoryBImpl,
    RepositoryBProtocol,
    RepositoryUnknownProtocol,
    ServiceAImpl,
    ServiceAProtocol,
    ServiceBImpl,
    Session,
    UseCaseAImpl,
)


class TestContainer:
    """
    Тесты контейнера зависимостей.
    """

    @staticmethod
    async def test_get_by_name_without_dependencies(
        container: ContainerProtocol,
    ) -> None:
        """
        Тестируем метод `get_by_name` для зависимости, которая ни от чего не зависит.
        """
        repository_a = await container.get_by_name('repository_a')
        assert isinstance(repository_a, RepositoryAImpl)

    @staticmethod
    async def test_get_by_name_unknown(container: ContainerProtocol) -> None:
        """
        Тестируем метод `get_by_name` для неизвестной зависимости.
        """
        with pytest.raises(ContainerError):
            await container.get_by_name('unknown_repository')

    @staticmethod
    async def test_get_by_type_without_dependencies(
        container: ContainerProtocol,
    ) -> None:
        """
        Тестируем метод `get_by_type` для зависимости, которая ни от чего не зависит.
        """
        repository_a = await container.get_by_type(RepositoryAProtocol)
        assert isinstance(repository_a, RepositoryAImpl)

    @staticmethod
    async def test_get_by_type_unknown(container: ContainerProtocol) -> None:
        """
        Тестируем метод `get_by_type` для неизвестной зависимости.
        """
        with pytest.raises(ContainerError):
            await container.get_by_type(RepositoryUnknownProtocol)

    @staticmethod
    async def test_get_by_name_with_dependencies(container: ContainerImpl) -> None:
        """
        Тестируем метод `get_by_name` для зависимости, которая зависит от других зависимостей.
        """
        with pytest.raises(ContainerError):
            await container.get_by_name('service_a')
        async with container:
            service_a = await container.get_by_name('service_a')
            assert isinstance(service_a, ServiceAImpl)
            assert ServiceAProtocol in container.instances
            assert isinstance(service_a.repository_a, RepositoryAImpl)
            assert RepositoryAProtocol not in container.instances
            assert isinstance(service_a.repository_b, RepositoryBImpl)
            assert RepositoryBProtocol in container.instances

    @staticmethod
    async def test_get_by_name_with_extra(container: ContainerProtocol) -> None:
        """
        Тестируем метод `get_by_name` для большого дерева зависимостей, содержащего дополнительные параметры.
        """
        expected_int_value = 10
        expected_str_value = 'str_value'
        session = Session()
        async with container:
            use_case_a = await container.get_by_name(
                'use_case_a',
                extra={
                    ('session', Session | None): session,
                    ('value', int): lambda: expected_int_value,
                    ('value', str): expected_str_value,
                },
            )
            assert isinstance(use_case_a, UseCaseAImpl)
            assert isinstance(use_case_a.service_a, ServiceAImpl)
            assert isinstance(use_case_a.service_a.repository_a, RepositoryAImpl)
            assert isinstance(use_case_a.service_a.repository_b, RepositoryBImpl)
            assert isinstance(use_case_a.service_b, ServiceBImpl)
            assert isinstance(use_case_a.service_b.repository_a, RepositoryAImpl)
            assert isinstance(use_case_a.service_b.repository_b, RepositoryBImpl)
            assert use_case_a.service_b.value == expected_int_value
            assert use_case_a.value == expected_str_value
            assert use_case_a.service_a.repository_a is not use_case_a.service_b.repository_a
            assert use_case_a.service_a.repository_b is use_case_a.service_b.repository_b
            assert session.in_transaction
        assert not session.in_transaction

    @staticmethod
    async def test_create_new_with_call(container: ContainerImpl) -> None:
        """
        Тестируем создание нового контейнера с помощью вызова.
        """
        expected_int_value = 10
        async with container({('value', int): expected_int_value}) as new_container:
            new_container = cast(ContainerImpl, new_container)
            assert container != new_container
            service_b = await new_container.get_by_name('service_b')
            assert isinstance(service_b, ServiceBImpl)
            assert service_b.value == expected_int_value
            assert new_container.instances
            assert not container.instances
