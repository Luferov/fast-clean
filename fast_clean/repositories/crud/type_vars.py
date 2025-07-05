"""
Модуль, содержащий переменные типов.
"""

import uuid
from typing import TypeVar

from fast_clean.db import BaseInt, BaseUUID
from fast_clean.schemas import (
    CreateSchema,
    CreateSchemaInt,
    ReadSchema,
    ReadSchemaInt,
    UpdateSchema,
    UpdateSchemaInt,
)

ModelBaseType = TypeVar('ModelBaseType', bound=BaseInt | BaseUUID)
CreateSchemaBaseType = TypeVar('CreateSchemaBaseType', bound=CreateSchemaInt | CreateSchema)
ReadSchemaBaseType = TypeVar('ReadSchemaBaseType', bound=ReadSchemaInt | ReadSchema)
UpdateSchemaBaseType = TypeVar('UpdateSchemaBaseType', bound=UpdateSchemaInt | UpdateSchema)
IdType = TypeVar('IdType', bound=int | uuid.UUID)
IdTypeContravariant = TypeVar('IdTypeContravariant', bound=int | uuid.UUID, contravariant=True)


ModelIntType = TypeVar('ModelIntType', bound=BaseInt)
CreateSchemaIntType = TypeVar('CreateSchemaIntType', bound=CreateSchemaInt)
ReadSchemaIntType = TypeVar('ReadSchemaIntType', bound=ReadSchemaInt)
UpdateSchemaIntType = TypeVar('UpdateSchemaIntType', bound=UpdateSchemaInt)


ModelType = TypeVar('ModelType', bound=BaseUUID)
CreateSchemaType = TypeVar('CreateSchemaType', bound=CreateSchema)
ReadSchemaType = TypeVar('ReadSchemaType', bound=ReadSchema)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=UpdateSchema)
