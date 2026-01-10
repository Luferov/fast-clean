"""
Package containing the repository for CRUD operations on models.

Two implementations are provided:
- InMemory
- Db
"""

import uuid
from collections.abc import Iterable, Sequence
from typing import Protocol, Self

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
    Base repository protocol for CRUD operations on models.
    """

    async def get(self: Self, id: IdTypeContravariant) -> ReadSchemaBaseType:
        """
        Get a model by identifier.
        """
        ...

    async def get_or_none(self: Self, id: IdTypeContravariant) -> ReadSchemaBaseType | None:
        """
        Get a model or None by identifier.
        """
        ...

    async def get_by_ids(
        self: Self, ids: Sequence[IdTypeContravariant], *, exact: bool = False
    ) -> list[ReadSchemaBaseType]:
        """
        Get a list of models by identifiers.
        """
        ...

    async def get_all(self: Self) -> list[ReadSchemaBaseType]:
        """
        Get all models.
        """
        ...

    async def paginate(
        self: Self,
        pagination: PaginationSchema,
        *,
        search: str | None = None,
        search_by: Iterable[str] | None = None,
        sorting: Iterable[str] | None = None,
    ) -> PaginationResultSchema[ReadSchemaBaseType]:
        """
        Get a list of models with pagination, search, and sorting.
        """
        ...

    async def create(self: Self, create_object: CreateSchemaBaseType) -> ReadSchemaBaseType:
        """
        Create a model.
        """
        ...

    async def bulk_create(self: Self, create_objects: list[CreateSchemaBaseType]) -> list[ReadSchemaBaseType]:
        """
        Create multiple models.
        """
        ...

    async def update(self: Self, update_object: UpdateSchemaBaseType) -> ReadSchemaBaseType:
        """
        Update a model.
        """
        ...

    async def bulk_update(self: Self, update_objects: list[UpdateSchemaBaseType]) -> None:
        """
        Update multiple models.
        """
        ...

    async def upsert(self: Self, create_object: CreateSchemaBaseType) -> ReadSchemaBaseType:
        """
        Create or update a model.
        """
        ...

    async def delete(self: Self, ids: Sequence[IdTypeContravariant]) -> None:
        """
        Delete models.
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
    Repository protocol for CRUD operations on old-type models.
    """

    ...


class CrudRepositoryProtocol(
    CrudRepositoryBaseProtocol[ReadSchemaBaseType, CreateSchemaType, UpdateSchemaType, uuid.UUID],
    Protocol[ReadSchemaBaseType, CreateSchemaType, UpdateSchemaType],
):
    """
    Repository protocol for CRUD operations on new-type models.
    """

    ...
