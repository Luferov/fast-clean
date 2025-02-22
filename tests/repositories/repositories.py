"""
Модуль, содержащий тестовые репозитории.
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
    Протокол репозитория для выполнения операций над моделями.
    """

    ...


class ModelInMemoryRepository(
    InMemoryCrudRepository[CrudParentModelReadSchema, CrudParentModelCreateSchema, CrudParentModelUpdateSchema]
):
    """
    Репозиторий для выполнения операций над моделями в памяти.
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
    Репозиторий для выполнения операций над моделями в базе данных.
    """

    __subtypes__ = (
        (CrudChildAModel, CrudChildAModelReadSchema, CrudChildAModelCreateSchema, CrudChildAModelUpdateSchema),
        (CrudChildBModel, CrudChildBModelReadSchema, CrudChildBModelCreateSchema, CrudChildBModelUpdateSchema),
    )
