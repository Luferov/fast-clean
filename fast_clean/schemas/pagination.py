"""
Модуль, содержащий схемы пагинации.
"""

from __future__ import annotations

from typing import Generic, Self, TypeVar

from pydantic import BaseModel, Field

from .request_response import ResponseSchema


class PaginationRequestSchema(BaseModel):
    """
    Схема запроса пагинации.
    """

    page: int = Field(gt=0)
    page_size: int = Field(gt=0)

    def to_pagination_schema(self: Self) -> PaginationSchema:
        """
        Преобразуем к схеме пагинации с помощью limit и offset.
        """
        return PaginationSchema(limit=self.page_size, offset=(self.page - 1) * self.page_size)


class AppliedPaginationResponseSchema(ResponseSchema):
    """
    Схема ответа примененной пагинации.
    """

    page: int
    page_size: int
    count: int


class PaginationResponseSchema(ResponseSchema):
    """
    Схема ответа пагинации.
    """

    pagination: AppliedPaginationResponseSchema


class PaginationSchema(BaseModel):
    """
    Схема пагинации с помощью limit и offset.
    """

    limit: int
    offset: int


T = TypeVar('T')


class PaginationResultSchema(BaseModel, Generic[T]):
    """
    Схема результата пагинации.
    """

    objects: list[T]
    count: int
