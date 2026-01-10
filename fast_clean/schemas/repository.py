"""
Module containing repository schemas.
"""

import uuid
from typing import Generic, TypeVar

from pydantic import BaseModel

IdType = TypeVar('IdType')


class CreateSchemaGeneric(BaseModel, Generic[IdType]):
    """
    Schema for creating a model.
    """

    id: IdType | None = None


class ReadSchemaGeneric(BaseModel, Generic[IdType]):
    """
    Schema for reading a model.
    """

    id: IdType


class UpdateSchemaGeneric(BaseModel, Generic[IdType]):
    """
    Schema for updating a model.
    """

    id: IdType


CreateSchemaInt = CreateSchemaGeneric[int]
ReadSchemaInt = ReadSchemaGeneric[int]
UpdateSchemaInt = UpdateSchemaGeneric[int]

CreateSchema = CreateSchemaGeneric[uuid.UUID]
ReadSchema = ReadSchemaGeneric[uuid.UUID]
UpdateSchema = UpdateSchemaGeneric[uuid.UUID]
