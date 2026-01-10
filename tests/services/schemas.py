"""
Module containing test schemas.
"""

import uuid

from pydantic import BaseModel


class ChildModelSchema(BaseModel):
    """
    Schema of the child test model for testing data loading from files.
    """

    id: uuid.UUID
    str_column: str
    int_column: int

    parent_id: uuid.UUID


class ParentModelSchema(BaseModel):
    """
    Schema of the parent test model for testing data loading from files.
    """

    id: uuid.UUID
    str_column: str
    int_column: int

    children: list[ChildModelSchema]
