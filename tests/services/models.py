"""
Модуль, содержащий тестовые модели.
"""

from __future__ import annotations

import uuid

from fast_clean.db import BaseUUID
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class SeedChildModel(BaseUUID):
    """
    Дочерняя тестовая модель для тестирования загрузки данных из файлов.
    """

    str_column: Mapped[str] = mapped_column(String(length=100), nullable=False)
    int_column: Mapped[int] = mapped_column(Integer, nullable=False)

    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('seed_parent_model.id'))

    parent: Mapped[SeedParentModel] = relationship(back_populates='children')


class SeedParentModel(BaseUUID):
    """
    Родительская тестовая модель для тестирования загрузки данных из файлов.
    """

    str_column: Mapped[str] = mapped_column(String(length=100), nullable=False)
    int_column: Mapped[int] = mapped_column(Integer, nullable=False)

    children: Mapped[list[SeedChildModel]] = relationship(back_populates='parent')
