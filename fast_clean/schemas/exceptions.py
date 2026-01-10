"""
Module containing exception schemas.
"""

from pydantic import BaseModel


class BusinessLogicExceptionSchema(BaseModel):
    """
    Base business logic exception schema.
    """

    type: str
    message: str
    traceback: str | None


class ModelAlreadyExistsErrorSchema(BusinessLogicExceptionSchema):
    """
    Schema of the error raised when attempting to create a model with an existing unique
    field.
    """

    field: str


class ValidationErrorSchema(BusinessLogicExceptionSchema):
    """
    Validation error schema.
    """

    fields: list[str]
