"""
Module containing test schemas.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from fast_clean.schemas import CreateSchema, ReadSchema, UpdateSchema

from .enums import CrudModelTypeEnum


class CrudParentModelCreateSchema(CreateSchema):
    """
    Schema for creating the parent test model.
    """

    str_column: str
    int_column: int
    type: str


class CrudParentModelReadSchema(ReadSchema):
    """
    Schema for reading the parent test model.
    """

    model_config = ConfigDict(frozen=True)

    str_column: str
    int_column: int
    type: str = CrudModelTypeEnum.PARENT


class CrudParentModelUpdateSchema(UpdateSchema):
    """
    Schema for updating the parent test model.
    """

    str_column: str | None = None
    int_column: int | None = None


class CrudChildAModelCreateSchema(CrudParentModelCreateSchema):
    """
    Schema for creating child test model A.
    """

    type: Literal[CrudModelTypeEnum.CHILD_A] = CrudModelTypeEnum.CHILD_A
    float_column: float


class CrudChildAModelReadSchema(CrudParentModelReadSchema):
    """
    Schema for reading child test model A.
    """

    type: Literal[CrudModelTypeEnum.CHILD_A] = CrudModelTypeEnum.CHILD_A
    float_column: float


class CrudChildAModelUpdateSchema(CrudParentModelUpdateSchema):
    """
    Schema for updating child test model A.
    """

    float_column: float


class CrudChildBModelCreateSchema(CrudParentModelCreateSchema):
    """
    Schema for creating child test model B.
    """

    type: Literal[CrudModelTypeEnum.CHILD_B] = CrudModelTypeEnum.CHILD_B
    bool_column: bool


class CrudChildBModelReadSchema(CrudParentModelReadSchema):
    """
    Schema for reading child test model B.
    """

    type: Literal[CrudModelTypeEnum.CHILD_B] = CrudModelTypeEnum.CHILD_B
    bool_column: bool


class CrudChildBModelUpdateSchema(CrudParentModelUpdateSchema):
    """
    Schema for updating child test model B.
    """

    bool_column: bool


class FileSchema(BaseModel):
    """
    File data schema.
    """

    name: str
    content: bytes


class DirectorySchema(BaseModel):
    """
    Directory data schema.
    """

    name: str
    children: list[DirectorySchema | FileSchema]


class MessageValueSchema(BaseModel):
    """
    Message values schema for streaming.
    """

    str_value: str
    int_value: int


class MessageSchema(BaseModel):
    """
    Schema of a message received via streaming.
    """

    topic: str
    key: str | None
    value: bytes | None
    headers: list[tuple[str, str]]
