"""
Модуль, содержащий тестовые схемы.
"""

from __future__ import annotations

from typing import Literal

from fast_clean.schemas import CreateSchema, ReadSchema, UpdateSchema
from pydantic import BaseModel, ConfigDict

from .enums import CrudModelTypeEnum


class CrudParentModelCreateSchema(CreateSchema):
    """
    Схема для создания родительской тестовой модели.
    """

    str_column: str
    int_column: int
    type: str


class CrudParentModelReadSchema(ReadSchema):
    """
    Схема для чтения родительской тестовой модели.
    """

    model_config = ConfigDict(frozen=True)

    str_column: str
    int_column: int
    type: str = CrudModelTypeEnum.PARENT


class CrudParentModelUpdateSchema(UpdateSchema):
    """
    Схема для обновления родительской тестовой модели.
    """

    str_column: str | None = None
    int_column: int | None = None


class CrudChildAModelCreateSchema(CrudParentModelCreateSchema):
    """
    Схема для создания дочерней тестовой модели A.
    """

    type: Literal[CrudModelTypeEnum.CHILD_A] = CrudModelTypeEnum.CHILD_A
    float_column: float


class CrudChildAModelReadSchema(CrudParentModelReadSchema):
    """
    Схема для чтения дочерней тестовой модели A.
    """

    type: Literal[CrudModelTypeEnum.CHILD_A] = CrudModelTypeEnum.CHILD_A
    float_column: float


class CrudChildAModelUpdateSchema(CrudParentModelUpdateSchema):
    """
    Схема для обновления дочерней тестовой модели A.
    """

    float_column: float


class CrudChildBModelCreateSchema(CrudParentModelCreateSchema):
    """
    Схема для создания дочерней тестовой модели B.
    """

    type: Literal[CrudModelTypeEnum.CHILD_B] = CrudModelTypeEnum.CHILD_B
    bool_column: bool


class CrudChildBModelReadSchema(CrudParentModelReadSchema):
    """
    Схема для чтения дочерней тестовой модели B.
    """

    type: Literal[CrudModelTypeEnum.CHILD_B] = CrudModelTypeEnum.CHILD_B
    bool_column: bool


class CrudChildBModelUpdateSchema(CrudParentModelUpdateSchema):
    """
    Схема для обновления дочерней тестовой модели B.
    """

    bool_column: bool


class FileSchema(BaseModel):
    """
    Схема данных файла.
    """

    name: str
    content: bytes


class DirectorySchema(BaseModel):
    """
    Схема данных директории.
    """

    name: str
    children: list[DirectorySchema | FileSchema]


class MessageValueSchema(BaseModel):
    """
    Схема значений сообщения для стриминга.
    """

    str_value: str
    int_value: int


class MessageSchema(BaseModel):
    """
    Схема сообщения, полученного с помощью стриминга.
    """

    topic: str
    key: str | None
    value: bytes | None
    headers: list[tuple[str, str]]
