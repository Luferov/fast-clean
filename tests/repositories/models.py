"""
Модуль, содержащий тестовые модели.
"""

import uuid

from fast_clean.db import Base
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import ChoiceType

from .enums import CrudModelTypeEnum


class CrudParentModel(Base):
    """
    Родительская тестовая модель для тестирования репозитория.
    """

    str_column: Mapped[str] = mapped_column(String(length=100), nullable=False)
    int_column: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[CrudModelTypeEnum] = mapped_column(ChoiceType(CrudModelTypeEnum, impl=String()))

    __mapper_args__ = {
        'polymorphic_identity': CrudModelTypeEnum.PARENT,
        'polymorphic_on': 'type',
    }


class CrudChildAModel(CrudParentModel):
    """
    Дочерня тестовая модель A для тестирования репозитория.
    """

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey('crud_parent_model.id'), primary_key=True)
    float_column: Mapped[float] = mapped_column(Float, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': CrudModelTypeEnum.CHILD_A,
    }


class CrudChildBModel(CrudParentModel):
    """
    Дочерняя тестовая модель B для тестирования репозитория.
    """

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey('crud_parent_model.id'), primary_key=True)
    bool_column: Mapped[bool] = mapped_column(Boolean, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': CrudModelTypeEnum.CHILD_B,
    }
