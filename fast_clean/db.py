"""
Модуль, содержащий функционал, связанный с базой данных.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncContextManager, Protocol, Self

import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy_utils.types.uuid import UUIDType
from stringcase import snakecase

from .settings import CoreDbSettingsSchema, CoreSettingsSchema

if TYPE_CHECKING:
    from .repositories import SettingsRepositoryProtocol

POSTGRES_INDEXES_NAMING_CONVENTION = {
    'ix': '%(column_0_label)s_idx',
    'uq': '%(table_name)s_%(column_0_name)s_key',
    'ck': '%(table_name)s_%(constraint_name)s_check',
    'fk': '%(table_name)s_%(column_0_name)s_fkey',
    'pk': '%(table_name)s_pkey',
}

metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


def make_async_engine(db_dsn: str, *, scheme: str = 'public', echo: bool = False) -> AsyncEngine:
    """
    Создаем асинхронный движок.
    """
    return create_async_engine(
        db_dsn,
        connect_args={'options': f'-csearch_path={scheme}'},
        echo=echo,
    )


def make_async_session_factory(
    db_dsn: str, *, scheme: str = 'public', echo: bool = False
) -> async_sessionmaker[AsyncSession]:
    """
    Создаем фабрику асинхронных сессий.
    """
    asyncio_engine = make_async_engine(db_dsn, scheme=scheme, echo=echo)
    return async_sessionmaker(asyncio_engine, expire_on_commit=False, autoflush=False)


class Base(AsyncAttrs, DeclarativeBase):
    """
    Базовая родительская модель.
    """

    __abstract__ = True

    metadata = metadata


class BaseUUID(Base):
    """
    Базовая родительская модель нового типа.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(binary=False),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return snakecase(cls.__name__)


class BaseInt(Base):
    """
    Базовая родительская модель старого типа.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)


    @declared_attr.directive
    def __tablename__(cls) -> str:
        return snakecase(cls.__name__)

class SessionFactory:
    """
    Фабрика сессий.
    """

    async_session_factory: async_sessionmaker[AsyncSession] | None = None

    @classmethod
    @asynccontextmanager
    async def make_async_session_static(
        cls, settings_repository: SettingsRepositoryProtocol
    ) -> AsyncIterator[AsyncSession]:
        """
        Создаем асинхронную сессию с помощью статической фабрики.
        """
        if cls.async_session_factory is None:
            cls.async_session_factory = await cls.make_async_session_factory(settings_repository)
        async with cls.async_session_factory() as session:
            yield session

    @classmethod
    @asynccontextmanager
    async def make_async_session_dynamic(
        cls, settings_repository: SettingsRepositoryProtocol
    ) -> AsyncIterator[AsyncSession]:
        """
        Создаем асинхронную сессию с помощью динамической фабрики.
        """
        async_session_factory = await cls.make_async_session_factory(settings_repository)
        async with async_session_factory() as session:
            yield session

    @staticmethod
    async def make_async_session_factory(
        settings_repository: SettingsRepositoryProtocol,
    ) -> async_sessionmaker[AsyncSession]:
        """
        Создаем фабрику асинхронных сессий.
        """
        settings = await settings_repository.get(CoreSettingsSchema)
        db_settings = await settings_repository.get(CoreDbSettingsSchema)
        return make_async_session_factory(db_settings.dsn, scheme=db_settings.scheme, echo=settings.debug)


class SessionManagerProtocol(Protocol):
    """
    Протокол менеджера сессий.
    """

    def get_session(self: Self, immediate: bool = True) -> AsyncContextManager[AsyncSession]:
        """
        Получаем сессию для выполнения запроса.
        """
        ...


class SessionManagerImpl:
    """
    Реализация менеджера сессий.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @asynccontextmanager
    async def get_session(self: Self, immediate: bool = True) -> AsyncIterator[AsyncSession]:
        """
        Получаем сессию для выполнения запроса.
        """
        if self.session.in_transaction():
            yield self.session
        else:
            async with self.session.begin():
                if immediate:
                    await self.session.execute(sa.text('SET CONSTRAINTS ALL IMMEDIATE'))
                yield self.session
