"""
Module containing exceptions.
"""

import traceback
import uuid
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from functools import partial
from typing import Self, TypeVar

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exception_handlers import http_exception_handler
from stringcase import camelcase, snakecase

from .enums import ModelActionEnum
from .schemas import BusinessLogicExceptionSchema, ModelAlreadyExistsErrorSchema, ValidationErrorSchema
from .settings import CoreSettingsSchema

ModelType = TypeVar('ModelType')


class ContainerError(Exception):
    """
    Dependency container error.
    """

    def __init__(self, message: str, *args: object) -> None:
        super().__init__(*args)
        self.message = message


class LockError(Exception):
    """
    Distributed lock error.
    """

    message = 'Errors acquiring or releasing a lock'


class BusinessLogicException(Exception, ABC):
    """
    Base business logic exception.
    """

    @property
    def type(self: Self) -> str:
        """
        Error type.
        """
        return snakecase(type(self).__name__.replace('Error', ''))

    @property
    @abstractmethod
    def message(self: Self) -> str:
        """
        Error message.
        """
        ...

    def __str__(self: Self) -> str:
        return self.message

    def get_schema(self: Self, debug: bool) -> BusinessLogicExceptionSchema:
        """
        Get the exception schema.
        """
        return BusinessLogicExceptionSchema(
            type=self.type,
            message=self.message,
            traceback=(''.join(traceback.format_exception(type(self), self, self.__traceback__)) if debug else None),
        )


class PermissionDeniedError(BusinessLogicException):
    """
    Error raised due to insufficient permissions to perform an action.
    """

    @property
    def message(self: Self) -> str:
        return 'Insufficient permissions to perform the action'


class ModelNotFoundError(BusinessLogicException):
    """
    Error raised when a model cannot be found.
    """

    def __init__(
        self,
        model: type[ModelType] | str,
        *args: object,
        model_id: int | uuid.UUID | str | Iterable[int | uuid.UUID | str] | None = None,
        model_name: str | Iterable[str] | None = None,
        message: str | None = None,
    ) -> None:
        super().__init__(*args)
        self.model = model
        self.model_id = model_id
        self.model_name = model_name
        self.custom_message = message

    @property
    def message(self: Self) -> str:
        if self.custom_message is not None:
            return self.custom_message
        message = f'Could not find model {self.model if isinstance(self.model, str) else self.model.__name__}'
        if self.model_id is not None:
            if isinstance(self.model_id, Iterable):
                return f'{message} by identifiers: [{", ".join(map(str, self.model_id))}]'
            return f'{message} by identifier: {self.model_id}'
        if self.model_name is not None:
            if isinstance(self.model_name, Iterable):
                return f'{message} by names: [{", ".join(self.model_name)}]'
            return f'{message} by name: {self.model_name}'
        return message


class ModelAlreadyExistsError(BusinessLogicException):
    """
    Error raised when attempting to create a model with an existing unique field.
    """

    def __init__(self, field: str, message: str, *args: object) -> None:
        super().__init__(*args)
        self.field = field
        self.custom_message = message

    @property
    def message(self: Self) -> str:
        return self.custom_message

    def get_schema(self: Self, debug: bool) -> BusinessLogicExceptionSchema:
        return ModelAlreadyExistsErrorSchema.model_validate(
            {**super().get_schema(debug).model_dump(), 'field': self.field}
        )


class ModelIntegrityError(BusinessLogicException):
    """
    Data integrity error when interacting with a model.
    """

    def __init__(self, model: type[ModelType] | str, action: ModelActionEnum, *args: object) -> None:
        super().__init__(*args)
        self.model = model
        self.action = action

    @property
    def message(self: Self) -> str:
        """
        Error message.
        """
        message = 'Data integrity error'
        model_name = self.model if isinstance(self.model, str) else self.model.__name__
        match self.action:
            case ModelActionEnum.INSERT:
                message += f' when creating model {model_name}'
            case ModelActionEnum.UPDATE:
                message += f' when updating model {model_name}'
            case ModelActionEnum.UPSERT:
                message += f' when creating or updating model {model_name}'
            case ModelActionEnum.DELETE:
                message += f' when deleting model {model_name}'
        return message


class ValidationError(BusinessLogicException):
    """
    Validation error.
    """

    def __init__(self, field: str | Sequence[str], custom_message: str, *args: object) -> None:
        super().__init__(*args)
        self.field = field
        self.custom_message = custom_message

    @property
    def fields(self: Self) -> Sequence[str]:
        """
        Error fields.
        """
        return [self.field] if isinstance(self.field, str) else self.field

    @property
    def message(self: Self) -> str:
        return self.custom_message

    def get_schema(self: Self, debug: bool) -> BusinessLogicExceptionSchema:
        return ValidationErrorSchema.model_validate(
            {
                **super().get_schema(debug).model_dump(),
                'fields': list(map(camelcase, self.fields)),
            }
        )


class SortingFieldNotFoundError(BusinessLogicException):
    """
    Error raised when a sorting field cannot be found.
    """

    def __init__(self, field: str, *args: object) -> None:
        super().__init__(*args)
        self.field = field

    @property
    def message(self: Self) -> str:
        return f'Could not find field for sorting: {self.field}'


async def business_logic_exception_handler(
    settings: CoreSettingsSchema, request: Request, exception: BusinessLogicException
) -> Response:
    """
    Handler for the base business logic exception.
    """
    return await http_exception_handler(
        request,
        HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[exception.get_schema(settings.debug).model_dump()],
        ),
    )


async def permission_denied_error_handler(
    settings: CoreSettingsSchema, request: Request, error: PermissionDeniedError
) -> Response:
    """
    Handler for the error raised due to insufficient permissions to perform an action.
    """
    return await http_exception_handler(
        request,
        HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=[error.get_schema(settings.debug).model_dump()],
        ),
    )


async def model_not_found_error_handler(
    settings: CoreSettingsSchema, request: Request, error: ModelNotFoundError
) -> Response:
    """
    Handler for the error raised when a model cannot be found.
    """
    return await http_exception_handler(
        request,
        HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[error.get_schema(settings.debug).model_dump()],
        ),
    )


async def model_already_exists_error_handler(
    settings: CoreSettingsSchema, request: Request, error: ModelAlreadyExistsError
) -> Response:
    """
    Handler for the error raised when attempting to create a model with an existing unique
    field.
    """
    return await http_exception_handler(
        request,
        HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=[error.get_schema(settings.debug).model_dump()],
        ),
    )


def use_exceptions_handlers(app: FastAPI, settings: CoreSettingsSchema) -> None:
    """
    Register global exception handlers.
    """
    app.exception_handler(BusinessLogicException)(partial(business_logic_exception_handler, settings))
    app.exception_handler(PermissionDeniedError)(partial(permission_denied_error_handler, settings))
    app.exception_handler(ModelNotFoundError)(partial(model_not_found_error_handler, settings))
    app.exception_handler(ModelAlreadyExistsError)(partial(model_already_exists_error_handler, settings))
