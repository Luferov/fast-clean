"""
Модуль, содержащий переменные типов.
"""

import uuid
from typing import TypeVar

from fast_clean.db import Base, BaseOld
from fast_clean.schemas import (
    CreateSchema,
    CreateSchemaOld,
    ReadSchema,
    ReadSchemaOld,
    UpdateSchema,
    UpdateSchemaOld,
)

ModelBaseType = TypeVar('ModelBaseType', bound=BaseOld | Base)
CreateSchemaBaseType = TypeVar('CreateSchemaBaseType', bound=CreateSchemaOld | CreateSchema)
ReadSchemaBaseType = TypeVar('ReadSchemaBaseType', bound=ReadSchemaOld | ReadSchema)
UpdateSchemaBaseType = TypeVar('UpdateSchemaBaseType', bound=UpdateSchemaOld | UpdateSchema)
IdType = TypeVar('IdType', bound=int | uuid.UUID)
IdTypeContravariant = TypeVar('IdTypeContravariant', bound=int | uuid.UUID, contravariant=True)


ModelOldType = TypeVar('ModelOldType', bound=BaseOld)
CreateSchemaOldType = TypeVar('CreateSchemaOldType', bound=CreateSchemaOld)
ReadSchemaOldType = TypeVar('ReadSchemaOldType', bound=ReadSchemaOld)
UpdateSchemaOldType = TypeVar('UpdateSchemaOldType', bound=UpdateSchemaOld)


ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=CreateSchema)
ReadSchemaType = TypeVar('ReadSchemaType', bound=ReadSchema)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=UpdateSchema)
