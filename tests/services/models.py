"""
Module containing test models.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fast_clean.db import Base


class SeedChildModel(Base):
    """
    Child test model for testing data loading from files.
    """

    __tablename__ = 'seed_child_model'

    str_column: Mapped[str] = mapped_column(String(length=100), nullable=False)
    int_column: Mapped[int] = mapped_column(Integer, nullable=False)

    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('seed_parent_model.id'))

    parent: Mapped[SeedParentModel] = relationship(back_populates='children')


class SeedParentModel(Base):
    """
    Parent test model for testing data loading from files.
    """

    __tablename__ = 'seed_parent_model'

    str_column: Mapped[str] = mapped_column(String(length=100), nullable=False)
    int_column: Mapped[int] = mapped_column(Integer, nullable=False)

    children: Mapped[list[SeedChildModel]] = relationship(back_populates='parent')
