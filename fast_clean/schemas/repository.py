"""
Модуль, содержащий схемы репозиториев.
"""

import uuid
from typing import Generic, TypeVar

from pydantic import BaseModel

IdType = TypeVar('IdType')


class CreateSchemaGeneric(BaseModel, Generic[IdType]):
    """
    Схема для создания модели.
    """

    id: IdType | None = None


class ReadSchemaGeneric(BaseModel, Generic[IdType]):
    """
    Схема для чтения модели.
    """

    id: IdType


class UpdateSchemaGeneric(BaseModel, Generic[IdType]):
    """
    Схема для обновления модели.
    """

    id: IdType


CreateSchemaInt = CreateSchemaGeneric[int]
ReadSchemaInt = ReadSchemaGeneric[int]
UpdateSchemaInt = UpdateSchemaGeneric[int]

CreateSchema = CreateSchemaGeneric[uuid.UUID]
ReadSchema = ReadSchemaGeneric[uuid.UUID]
UpdateSchema = UpdateSchemaGeneric[uuid.UUID]
