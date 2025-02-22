"""
Модуль, содержащий исключения.
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
    Ошибка контейнера зависимостей.
    """

    def __init__(self, message: str, *args: object) -> None:
        super().__init__(*args)
        self.message = message


class LockError(Exception):
    """
    Ошибка распределенной блокировки.
    """

    message = 'Errors acquiring or releasing a lock'


class BusinessLogicException(Exception, ABC):
    """
    Базовое исключение бизнес-логики.
    """

    @property
    def type(self: Self) -> str:
        """
        Тип ошибки.
        """
        return snakecase(type(self).__name__.replace('Error', ''))

    @property
    @abstractmethod
    def msg(self: Self) -> str:
        """
        Сообщение ошибки.
        """
        ...

    def __str__(self: Self) -> str:
        return self.msg

    def get_schema(self: Self, debug: bool) -> BusinessLogicExceptionSchema:
        """
        Получаем схему исключения.
        """
        return BusinessLogicExceptionSchema(
            type=self.type,
            msg=self.msg,
            traceback=(''.join(traceback.format_exception(type(self), self, self.__traceback__)) if debug else None),
        )


class PermissionDeniedError(BusinessLogicException):
    """
    Ошибка, возникающая при недостатке прав для выполнения действия.
    """

    @property
    def msg(self: Self) -> str:
        return 'Недостаточно прав для выполнения действия'


class ModelNotFoundError(BusinessLogicException):
    """
    Ошибка, возникающая при невозможности найти модель.
    """

    def __init__(
        self,
        model: type[ModelType] | str,
        *args: object,
        model_id: int | uuid.UUID | Iterable[int | uuid.UUID] | None = None,
        model_name: str | Iterable[str] | None = None,
        message: str | None = None,
    ) -> None:
        super().__init__(*args)
        self.model = model
        self.model_id = model_id
        self.model_name = model_name
        self.custom_message = message

    @property
    def msg(self: Self) -> str:
        if self.custom_message is not None:
            return self.custom_message
        msg = f'Не удалось найти модель {self.model if isinstance(self.model, str) else self.model.__name__}'
        if self.model_id is not None:
            if isinstance(self.model_id, Iterable):
                return f'{msg} по идентификаторам: [{", ".join(map(str, self.model_id))}]'
            return f'{msg} по идентификатору: {self.model_id}'
        if self.model_name is not None:
            if isinstance(self.model_name, Iterable):
                return f'{msg} по именам: [{", ".join(self.model_name)}]'
            return f'{msg} по имени: {self.model_name}'
        return msg


class ModelAlreadyExistsError(BusinessLogicException):
    """
    Ошибка, возникающая при попытке создать модель с существующим уникальным полем.
    """

    def __init__(self, field: str, message: str, *args: object) -> None:
        super().__init__(*args)
        self.field = field
        self.message = message

    @property
    def msg(self: Self) -> str:
        return self.message

    def get_schema(self: Self, debug: bool) -> BusinessLogicExceptionSchema:
        return ModelAlreadyExistsErrorSchema.model_validate(
            {**super().get_schema(debug).model_dump(), 'field': self.field}
        )


class ModelIntegrityError(BusinessLogicException):
    """
    Ошибка целостности данных при взаимодействии с моделью.
    """

    def __init__(self, model: type[ModelType] | str, action: ModelActionEnum, *args: object) -> None:
        super().__init__(*args)
        self.model = model
        self.action = action

    @property
    def msg(self: Self) -> str:
        """
        Сообщение ошибки.
        """
        msg = 'Ошибка целостности данных'
        model_name = self.model if isinstance(self.model, str) else self.model.__name__
        match self.action:
            case ModelActionEnum.INSERT:
                msg += f' при создании модели {model_name}'
            case ModelActionEnum.UPDATE:
                msg += f' при изменении модели {model_name}'
            case ModelActionEnum.UPSERT:
                msg += f' при создании или изменении модели {model_name}'
            case ModelActionEnum.DELETE:
                msg += f' при удалении модели {model_name}'
        return msg


class ValidationError(BusinessLogicException):
    """
    Ошибка валидации.
    """

    def __init__(self, field: str | Sequence[str], message: str, *args: object) -> None:
        super().__init__(*args)
        self.field = field
        self.message = message

    @property
    def fields(self: Self) -> Sequence[str]:
        """
        Поля ошибки.
        """
        return [self.field] if isinstance(self.field, str) else self.field

    @property
    def msg(self: Self) -> str:
        return self.message

    def get_schema(self: Self, debug: bool) -> BusinessLogicExceptionSchema:
        return ValidationErrorSchema.model_validate(
            {
                **super().get_schema(debug).model_dump(),
                'fields': list(map(camelcase, self.fields)),
            }
        )


class SortingFieldNotFoundError(BusinessLogicException):
    """
    Ошибка, возникающая при невозможности найти поле для сортировки.
    """

    def __init__(self, field: str, *args: object) -> None:
        super().__init__(*args)
        self.field = field

    @property
    def msg(self: Self) -> str:
        return f'Не удалось найти поле для сортировки: {self.field}'


async def business_logic_exception_handler(
    settings: CoreSettingsSchema, request: Request, exception: BusinessLogicException
) -> Response:
    """
    Обработчик базового исключения бизнес-логики.
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
    Обработчик ошибки, возникающей при недостатке прав для выполнения действия.
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
    Обработчик ошибки, возникающей при невозможности найти модель.
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
    Обработчик ошибки, возникающей при попытке создать модель с существующим уникальным
    полем.
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
    Регистрируем глобальные обработчики исключений.
    """
    app.exception_handler(BusinessLogicException)(partial(business_logic_exception_handler, settings))
    app.exception_handler(PermissionDeniedError)(partial(permission_denied_error_handler, settings))
    app.exception_handler(ModelNotFoundError)(partial(model_not_found_error_handler, settings))
    app.exception_handler(ModelAlreadyExistsError)(partial(model_already_exists_error_handler, settings))
