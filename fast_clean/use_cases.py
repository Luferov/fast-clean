"""
Модуль, содержащий варианты использования.
"""

from __future__ import annotations

from types import new_class
from typing import Any, Protocol, TypeVar, cast

UseCaseResultSchemaType = TypeVar('UseCaseResultSchemaType', covariant=True)


class UseCaseProtocol(Protocol[UseCaseResultSchemaType]):
    """
    Протокол варианта использования.
    """

    async def __call__(self) -> UseCaseResultSchemaType:
        """
        Вызываем вариант использования.
        """
        ...

    def __class_getitem__(cls, params: type | tuple[type, ...]) -> type:
        """
        Создаем уникальный класс.

        По умолчанию одинаковые обобщенные классы указывают на один и тот же _GenericAlias.
        Из-за данного поведения поиск по типу становится невозможным.

            UseCaseA = UseCaseProtocol[None]
            UseCaseB = UseCaseProtocol[None]
            assert UseCaseA is UseCaseB

        Поэтому вместо _GenericAlias возвращаем уникального наследника.
        """
        generic_alias = cast(Any, super()).__class_getitem__(params)
        return new_class(cls.__name__, (generic_alias,))
