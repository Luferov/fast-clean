"""
Модуль, содержащий тестовые схемы.
"""

import uuid

from pydantic import BaseModel


class ChildModelSchema(BaseModel):
    """
    Схема дочерней тестовой модели для тестирования загрузки данных из файлов.
    """

    id: uuid.UUID
    str_column: str
    int_column: int

    parent_id: uuid.UUID


class ParentModelSchema(BaseModel):
    """
    Схема родительской тестовой модели для тестирования загрузки данных из файлов.
    """

    id: uuid.UUID
    str_column: str
    int_column: int

    children: list[ChildModelSchema]
