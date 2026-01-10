"""
Module containing pagination schemas.
"""

from __future__ import annotations

from typing import Generic, Self, TypeVar

from pydantic import BaseModel, Field

from .request_response import RequestResponseSchema


class PaginationRequestSchema(BaseModel):
    """
    Pagination request schema.
    """

    page: int = Field(gt=0)
    page_size: int = Field(gt=0)

    def to_pagination_schema(self: Self) -> PaginationSchema:
        """
        Convert to a pagination schema using limit and offset.
        """
        return PaginationSchema(limit=self.page_size, offset=(self.page - 1) * self.page_size)


class AppliedPaginationResponseSchema(RequestResponseSchema):
    """
    Applied pagination response schema.
    """

    page: int
    page_size: int
    count: int


class PaginationResponseSchema(RequestResponseSchema):
    """
    Pagination response schema.
    """

    pagination: AppliedPaginationResponseSchema


class PaginationSchema(BaseModel):
    """
    Pagination schema using limit and offset.
    """

    limit: int
    offset: int


T = TypeVar('T')


class PaginationResultSchema(BaseModel, Generic[T]):
    """
    Pagination result schema.
    """

    objects: list[T]
    count: int
