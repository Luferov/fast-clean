"""
Модуль, содержащий схемы исключений.
"""

from pydantic import BaseModel


class BusinessLogicExceptionSchema(BaseModel):
    """
    Схема базового исключения бизнес-логики.
    """

    type: str
    msg: str
    traceback: str | None


class ModelAlreadyExistsErrorSchema(BusinessLogicExceptionSchema):
    """
    Схема ошибки, возникающей при попытке создать модель с существующим уникальным
    полем.
    """

    field: str


class ValidationErrorSchema(BusinessLogicExceptionSchema):
    """
    Схема ошибки валидации.
    """

    fields: list[str]
