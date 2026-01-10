"""
Module containing test repositories.
"""

from typing import Protocol

from fast_clean.repositories.crud import (
    CrudRepositoryProtocol,
    DbCrudRepository,
    InMemoryCrudRepository,
)

from .models import CrudChildAModel, CrudChildBModel, CrudParentModel
from .schemas import (
    CrudChildAModelCreateSchema,
    CrudChildAModelReadSchema,
    CrudChildAModelUpdateSchema,
    CrudChildBModelCreateSchema,
    CrudChildBModelReadSchema,
    CrudChildBModelUpdateSchema,
    CrudParentModelCreateSchema,
    CrudParentModelReadSchema,
    CrudParentModelUpdateSchema,
)


class ModelRepositoryProtocol(
    CrudRepositoryProtocol[CrudParentModelReadSchema, CrudParentModelCreateSchema, CrudParentModelUpdateSchema],
    Protocol,
):
    """
    Repository protocol for operations on models.
    """

    ...


class ModelInMemoryRepository(
    InMemoryCrudRepository[CrudParentModelReadSchema, CrudParentModelCreateSchema, CrudParentModelUpdateSchema]
):
    """
    Repository for operations on models in memory.
    """

    __subtypes__ = (
        (CrudChildAModelReadSchema, CrudChildAModelCreateSchema, CrudChildAModelUpdateSchema),
        (CrudChildBModelReadSchema, CrudChildBModelCreateSchema, CrudChildBModelUpdateSchema),
    )


class ModelDbRepository(
    DbCrudRepository[
        CrudParentModel, CrudParentModelReadSchema, CrudParentModelCreateSchema, CrudParentModelUpdateSchema
    ]
):
    """
    Repository for operations on models in the database.
    """

    __subtypes__ = (
        (CrudChildAModel, CrudChildAModelReadSchema, CrudChildAModelCreateSchema, CrudChildAModelUpdateSchema),
        (CrudChildBModel, CrudChildBModelReadSchema, CrudChildBModelCreateSchema, CrudChildBModelUpdateSchema),
    )
