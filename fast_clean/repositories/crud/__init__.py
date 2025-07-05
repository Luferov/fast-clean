"""
Пакет, содержащий репозиторий для выполнения CRUD операций над моделями.

Представлено две реализации:
- InMemory
- Db
"""

import uuid
from collections.abc import Iterable, Sequence
from typing import Any, Protocol, Self

from fast_clean.schemas import PaginationResultSchema, PaginationSchema

from .db import DbCrudRepository as DbCrudRepository
from .db import DbCrudRepositoryInt as DbCrudRepositoryInt
from .in_memory import InMemoryCrudRepository as InMemoryCrudRepository
from .in_memory import InMemoryCrudRepositoryInt as InMemoryCrudRepositoryInt
from .type_vars import (
    CreateSchemaBaseType,
    CreateSchemaIntType,
    CreateSchemaType,
    IdTypeContravariant,
    ReadSchemaBaseType,
    ReadSchemaIntType,
    UpdateSchemaBaseType,
    UpdateSchemaIntType,
    UpdateSchemaType,
)


class CrudRepositoryBaseProtocol(
    Protocol[
        ReadSchemaBaseType,
        CreateSchemaBaseType,
        UpdateSchemaBaseType,
        IdTypeContravariant,
    ]
):
    """
    Протокол базового репозитория для выполнения CRUD операций над моделями.
    """

    async def get(self: Self, id: IdTypeContravariant) -> ReadSchemaBaseType:
        """
        Получаем модель по идентификатору.
        """
        ...

    async def get_or_none(self: Self, id: IdTypeContravariant) -> ReadSchemaBaseType | None:
        """
        Получаем модель или None по идентификатору.
        """
        ...

    async def get_by_ids(
        self: Self, ids: Sequence[IdTypeContravariant], *, exact: bool = False
    ) -> list[ReadSchemaBaseType]:
        """
        Получаем список моделей по идентификаторам.
        """
        ...

    async def get_all(self: Self) -> list[ReadSchemaBaseType]:
        """
        Получаем все модели.
        """
        ...

    async def paginate(
        self: Self,
        pagination: PaginationSchema,
        user: Any,
        policies: list[str],
        *,
        search: str | None = None,
        search_by: Iterable[str] | None = None,
        sorting: Iterable[str] | None = None,
    ) -> PaginationResultSchema[ReadSchemaBaseType]:
        """
        Получаем список моделей с пагинацией, поиском и сортировкой.
        """
        ...

    async def create(self: Self, create_object: CreateSchemaBaseType) -> ReadSchemaBaseType:
        """
        Создаем модель.
        """
        ...

    async def bulk_create(self: Self, create_objects: list[CreateSchemaBaseType]) -> list[ReadSchemaBaseType]:
        """
        Создаем несколько моделей.
        """
        ...

    async def update(self: Self, update_object: UpdateSchemaBaseType) -> ReadSchemaBaseType:
        """
        Обновляем модель.
        """
        ...

    async def bulk_update(self: Self, update_objects: list[UpdateSchemaBaseType]) -> None:
        """
        Обновляем несколько моделей.
        """
        ...

    async def upsert(self: Self, create_object: CreateSchemaBaseType) -> ReadSchemaBaseType:
        """
        Создаем или обновляем модель.
        """
        ...

    async def delete(self: Self, ids: Sequence[IdTypeContravariant]) -> None:
        """
        Удаляем модели.
        """
        ...


class CrudRepositoryIntProtocol(
    CrudRepositoryBaseProtocol[
        ReadSchemaIntType,
        CreateSchemaIntType,
        UpdateSchemaIntType,
        int,
    ],
    Protocol[
        ReadSchemaIntType,
        CreateSchemaIntType,
        UpdateSchemaIntType,
    ],
):
    """
    Протокол репозитория для выполнения CRUD операций над моделями старого типа.
    """

    ...


class CrudRepositoryProtocol(
    CrudRepositoryBaseProtocol[ReadSchemaBaseType, CreateSchemaType, UpdateSchemaType, uuid.UUID],
    Protocol[ReadSchemaBaseType, CreateSchemaType, UpdateSchemaType],
):
    """
    Протокол репозитория для выполнения CRUD операций над моделями нового типа.
    """

    ...
