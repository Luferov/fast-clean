"""
Модуль, содержащий репозиторий для выполнения CRUD операций над моделями в базе данных.
"""

from __future__ import annotations

import contextlib
import uuid
from collections.abc import Callable, Iterable, Sequence
from itertools import groupby
from typing import Any, Generic, Self, cast, get_args

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectin_polymorphic
from sqlalchemy.sql.expression import func

from fast_clean.db import SessionManagerProtocol
from fast_clean.enums import ModelActionEnum
from fast_clean.exceptions import (
    ModelIntegrityError,
    ModelNotFoundError,
    SortingFieldNotFoundError,
)
from fast_clean.schemas import PaginationResultSchema, PaginationSchema

from .type_vars import (
    CreateSchemaBaseType,
    CreateSchemaIntType,
    CreateSchemaType,
    IdType,
    ModelBaseType,
    ModelIntType,
    ModelType,
    ReadSchemaBaseType,
    ReadSchemaIntType,
    ReadSchemaType,
    UpdateSchemaBaseType,
    UpdateSchemaIntType,
    UpdateSchemaType,
)


class DbCrudRepositoryBase(
    Generic[
        ModelBaseType,
        ReadSchemaBaseType,
        CreateSchemaBaseType,
        UpdateSchemaBaseType,
        IdType,
    ]
):
    """
    Базовый репозиторий для выполнения CRUD операций над моделями в базе данных.
    """

    __abstract__: bool = True

    __orig_bases__: tuple[
        type[
            DbCrudRepositoryBase[ModelBaseType, ReadSchemaBaseType, CreateSchemaBaseType, UpdateSchemaBaseType, IdType]
        ]
    ]
    __subtypes__: Sequence[
        tuple[type[ModelBaseType], type[ReadSchemaBaseType], type[CreateSchemaBaseType], type[UpdateSchemaBaseType]]
    ]

    model_types: set[type[ModelBaseType]] = set()
    model_subtypes: set[type[ModelBaseType]] = set()
    model_types_mapping: dict[type[ModelBaseType], type[ReadSchemaBaseType]]
    create_models_mapping: dict[type[CreateSchemaBaseType], type[ModelBaseType]]
    update_models_mapping: dict[type[UpdateSchemaBaseType], type[ModelBaseType]]
    model_identities_mapping: dict[Any, type[ModelBaseType]] = {}

    model_type: type[ModelBaseType]

    def __init__(self, session_manager: SessionManagerProtocol):
        if self.__dict__.get('__abstract__', False):
            raise TypeError(f"Can't instantiate abstract class {type(self).__name__}")
        self.session_manager = session_manager

    def __init_subclass__(cls) -> None:
        """
        Инициализируем класс.

        Получаем используемую модель SQLAlchemy и схему Pydantic из базового типа.
        """
        if cls.__dict__.get('__abstract__', False):
            return super().__init_subclass__()

        base_repository_generic = next(
            (
                base
                for base in getattr(cls, '__orig_bases__', [])
                if issubclass(getattr(base, '__origin__', base), DbCrudRepositoryBase)
            ),
            None,
        )
        if not base_repository_generic:
            raise ValueError('Repository must be implemented by DbCrudRepositoryBase')

        if not hasattr(cls, '__subtypes__'):
            cls.__subtypes__ = []

        cls.model_subtypes = {st[0] for st in cls.__subtypes__}

        cls.model_types_mapping = {}
        cls.create_models_mapping = {}
        cls.update_models_mapping = {}
        cls.model_identities_mapping = {}
        types: Sequence[
            tuple[type[ModelBaseType], type[ReadSchemaBaseType], type[CreateSchemaBaseType], type[UpdateSchemaBaseType]]
        ] = [*cls.__subtypes__, get_args(base_repository_generic)[:4]]
        for model_type, read_schema_type, create_schema_type, update_schema_type in types:
            cls.model_types.add(model_type)
            cls.model_types_mapping[model_type] = read_schema_type
            cls.create_models_mapping[create_schema_type] = model_type
            cls.update_models_mapping[update_schema_type] = model_type
            cls.model_identities_mapping[model_type.__mapper__.polymorphic_identity] = model_type

        cls.model_type, *_ = cast(
            tuple[
                type[ModelBaseType],
                type[ReadSchemaBaseType],
                type[CreateSchemaBaseType],
                type[UpdateSchemaBaseType],
            ],
            get_args(base_repository_generic),
        )

        return super().__init_subclass__()

    async def get(self: Self, id: IdType) -> ReadSchemaBaseType:
        """
        Получаем модель по идентификатору.
        """
        async with self.session_manager.get_session() as s:
            statement = self.select().where(self.model_type.id == id)
            model = (await s.execute(statement)).scalar_one_or_none()
            if model is None:
                raise ModelNotFoundError(self.model_type, model_id=id)
            return self.model_validate(model)

    async def get_or_none(self: Self, id: IdType) -> ReadSchemaBaseType | None:
        """
        Получаем модель или None по идентификатору.
        """
        with contextlib.suppress(ModelNotFoundError):
            return await self.get(id)
        return None

    async def get_by_ids(self: Self, ids: Sequence[IdType], *, exact: bool = False) -> list[ReadSchemaBaseType]:
        """
        Получаем список моделей по идентификаторам.
        """
        async with self.session_manager.get_session() as s:
            statement = self.select().where(self.model_type.id.in_(ids))
            models = (await s.execute(statement)).scalars().all()
            self.check_get_by_ids_exact(ids, models, exact)
            return [self.model_validate(model) for model in models]

    async def get_all(self: Self) -> list[ReadSchemaBaseType]:
        """
        Получаем все модели.
        """
        async with self.session_manager.get_session() as s:
            statement = self.select()
            models = (await s.execute(statement)).scalars().all()
            return [self.model_validate(model) for model in models]

    async def paginate(
        self: Self,
        pagination: PaginationSchema,
        user: Any,
        policies: list[str],
        *,
        search: str | None = None,
        search_by: Iterable[str] | None = None,
        sorting: Iterable[str] | None = None,
    ) -> PaginationResultSchema[ReadSchemaBaseType]:
        """
        Получаем список моделей с пагинацией, поиском и сортировкой.
        """
        return await self.paginate_with_filter(
            pagination,
            user,
            policies,
            search=search,
            search_by=search_by,
            sorting=sorting,
        )

    async def create(self: Self, create_object: CreateSchemaBaseType) -> ReadSchemaBaseType:
        """
        Создаем модель.
        """
        async with self.session_manager.get_session() as s:
            try:
                model_type = self.create_models_mapping[type(create_object)]
                create_dict = self.dump_create_object(create_object)
                return (await self.bulk_create_with_model_type(model_type, [create_dict], s))[0]
            except IntegrityError as integrity_error:
                raise ModelIntegrityError(self.model_type, ModelActionEnum.INSERT) from integrity_error

    async def bulk_create(self: Self, create_objects: list[CreateSchemaBaseType]) -> list[ReadSchemaBaseType]:
        """
        Создаем несколько моделей.
        """
        if len(create_objects) == 0:
            return []
        async with self.session_manager.get_session() as s:
            try:
                created_models: list[ReadSchemaBaseType] = []
                for model_type, type_create_objects in groupby(
                    create_objects, key=lambda co: self.create_models_mapping[type(co)]
                ):
                    create_dicts = [self.dump_create_object(create_object) for create_object in type_create_objects]
                    created_models.extend(await self.bulk_create_with_model_type(model_type, create_dicts, s))
                return created_models
            except IntegrityError as integrity_error:
                raise ModelIntegrityError(self.model_type, ModelActionEnum.INSERT) from integrity_error

    async def update(self: Self, update_object: UpdateSchemaBaseType) -> ReadSchemaBaseType:
        """
        Обновляем модель.
        """
        async with self.session_manager.get_session() as s:
            try:
                model_type = self.update_models_mapping[type(update_object)]
                update_dict = update_object.model_dump(exclude_unset=True)
                return await self.update_with_model_type(model_type, update_dict, s)
            except IntegrityError as integrity_error:
                raise ModelIntegrityError(self.model_type, ModelActionEnum.UPDATE) from integrity_error

    async def bulk_update(self: Self, update_objects: list[UpdateSchemaBaseType]) -> None:
        """
        Обновляем несколько моделей.
        """
        if len(update_objects) == 0:
            return
        async with self.session_manager.get_session() as s:
            try:
                for model_type, type_update_objects in groupby(
                    update_objects, key=lambda co: self.update_models_mapping[type(co)]
                ):
                    update_dicts = [update_object.model_dump() for update_object in type_update_objects]
                    await self.bulk_update_with_model_type(model_type, update_dicts, s)
            except IntegrityError as integrity_error:
                raise ModelIntegrityError(self.model_type, ModelActionEnum.UPDATE) from integrity_error

    async def upsert(self: Self, create_object: CreateSchemaBaseType) -> ReadSchemaBaseType:
        """
        Создаем или обновляем модель.
        """
        async with self.session_manager.get_session() as s:
            try:
                model_type = self.create_models_mapping[type(create_object)]
                create_dict = self.dump_create_object(create_object)
                return await self.upsert_with_model_type(model_type, create_dict, s)
            except IntegrityError as integrity_error:
                raise ModelIntegrityError(self.model_type, ModelActionEnum.UPSERT) from integrity_error

    async def delete(self: Self, ids: Sequence[IdType]) -> None:
        """
        Удаляем модели.
        """
        if len(ids) == 0:
            return
        async with self.session_manager.get_session() as s:
            try:
                model_types: list[type[ModelBaseType]] = [self.model_type]
                if self.model_type.__mapper__.polymorphic_on is not None:
                    types_statement = (
                        sa.select(self.model_type.__mapper__.polymorphic_on)
                        .where(self.model_type.id.in_(ids))
                        .distinct()
                    )
                    types = (await s.execute(types_statement)).scalars().all()
                    for t in types:
                        model_types.append(self.model_identities_mapping[t])
                for model_type in model_types[::-1]:
                    statement = sa.delete(model_type).where(model_type.id.in_(ids))
                    await s.execute(statement)
            except IntegrityError as integrity_error:
                raise ModelIntegrityError(self.model_type, ModelActionEnum.DELETE) from integrity_error

    @classmethod
    def select(cls) -> sa.Select[tuple[ModelBaseType]]:
        """
        Выбираем базовую модели или наследника со всеми полями при наличии.
        """
        statement = sa.select(cls.model_type)
        if cls.model_subtypes:
            return statement.options(selectin_polymorphic(cls.model_type, cls.model_subtypes))
        return statement

    @classmethod
    def model_validate(cls, model: ModelBaseType) -> ReadSchemaBaseType:
        """
        Приводим модель к схеме.
        """
        read_schema_type = cls.model_types_mapping[type(model)]
        return cast(
            ReadSchemaBaseType,
            read_schema_type.model_validate(model, from_attributes=True),
        )

    @classmethod
    async def bulk_create_with_model_type(
        cls, model_type: type[ModelBaseType], create_dicts: list[dict[str, Any]], session: AsyncSession
    ) -> list[ReadSchemaBaseType]:
        """
        Создаем модели с помощью типа.
        """
        parent_dicts = await cls.bulk_create_parent_model(model_type, create_dicts, session)
        values: list[dict[str, Any]] = []
        for create_dict, parent_dict in zip(create_dicts, parent_dicts, strict=True):
            value = {k: v for k, v in create_dict.items() if k in model_type.__table__.columns}
            if 'id' in parent_dict:
                value['id'] = parent_dict['id']
            values.append(value)
        statement = sa.insert(model_type).values(values).returning(*model_type.__table__.columns.values())
        model_dicts = (await session.execute(statement)).mappings().all()
        read_schema_type = cls.model_types_mapping[model_type]
        return [
            cast(
                ReadSchemaBaseType,
                read_schema_type.model_validate({**parent_dict, **model_dict}),
            )
            for parent_dict, model_dict in zip(parent_dicts, model_dicts, strict=True)
        ]

    @classmethod
    async def bulk_create_parent_model(
        cls, model_type: type[ModelBaseType], create_dicts: list[dict[str, Any]], session: AsyncSession
    ) -> list[dict[str, Any]]:
        """
        Создаем родительские модели с помощью типа.
        """
        parent_model_type = cls.get_parent_model_type(model_type)
        if parent_model_type is None:
            return [{} for _ in create_dicts]
        return [
            ps.model_dump() for ps in await cls.bulk_create_with_model_type(parent_model_type, create_dicts, session)
        ]

    @classmethod
    async def update_with_model_type(
        cls, model_type: type[ModelBaseType], update_dict: dict[str, Any], session: AsyncSession
    ) -> ReadSchemaBaseType:
        """
        Обновляем модель с помощью типа.
        """
        parent_dict = await cls.update_parent_model(model_type, update_dict, session)
        statement = (
            sa.update(model_type)
            .where(model_type.id == update_dict['id'])
            .values({k: v for k, v in update_dict.items() if k in model_type.__table__.columns if k != 'id'})
            .returning(*model_type.__table__.columns.values())
        )
        model_dict = (await session.execute(statement)).mappings().one()
        read_schema_type = cls.model_types_mapping[model_type]
        return cast(
            ReadSchemaBaseType,
            read_schema_type.model_validate({**parent_dict, **model_dict}),
        )

    @classmethod
    async def update_parent_model(
        cls, model_type: type[ModelBaseType], update_dict: dict[str, Any], session: AsyncSession
    ) -> dict[str, Any]:
        """
        Обновляем родительскую модель с помощью типа.
        """
        parent_model_type = cls.get_parent_model_type(model_type)
        if parent_model_type is None:
            return {}
        return (await cls.update_with_model_type(parent_model_type, update_dict, session)).model_dump()

    @classmethod
    async def bulk_update_with_model_type(
        cls, model_type: type[ModelBaseType], update_dicts: list[dict[str, Any]], session: AsyncSession
    ) -> None:
        """
        Создаем модели с помощью типа.
        """
        await cls.bulk_update_parent_model(model_type, update_dicts, session)
        values: list[dict[str, Any]] = []
        for update_dict in update_dicts:
            values.append({k: v for k, v in update_dict.items() if k in model_type.__table__.columns})
        statement = sa.update(model_type)
        await session.execute(statement, values)

    @classmethod
    async def bulk_update_parent_model(
        cls, model_type: type[ModelBaseType], update_dicts: list[dict[str, Any]], session: AsyncSession
    ) -> None:
        """
        Обновляем родительские модели с помощью типа.
        """
        parent_model_type = cls.get_parent_model_type(model_type)
        if parent_model_type is not None:
            await cls.bulk_update_with_model_type(parent_model_type, update_dicts, session)

    @classmethod
    async def upsert_with_model_type(
        cls, model_type: type[ModelBaseType], create_dict: dict[str, Any], session: AsyncSession
    ) -> ReadSchemaBaseType:
        """
        Создаем или обновляем модель с помощью типа.
        """
        parent_dict = await cls.upsert_parent_model(model_type, create_dict, session)
        primary_keys = {key.name for key in cast(Any, sa.inspect(model_type)).primary_key}
        values = {k: v for k, v in create_dict.items() if k in model_type.__table__.columns}
        statement = (
            insert(model_type)
            .values(values)
            .on_conflict_do_update(
                index_elements=primary_keys,
                set_={k: v for k, v in values.items() if k not in primary_keys},
            )
            .returning(*model_type.__table__.columns.values())
        )
        model_dict = (await session.execute(statement)).mappings().one()
        read_schema_type = cls.model_types_mapping[model_type]
        return cast(
            ReadSchemaBaseType,
            read_schema_type.model_validate({**parent_dict, **model_dict}),
        )

    @classmethod
    async def upsert_parent_model(
        cls, model_type: type[ModelBaseType], create_dict: dict[str, Any], session: AsyncSession
    ) -> dict[str, Any]:
        """
        Создаем или обновляем родительскую модель с помощью типа.
        """
        parent_model_type = cls.get_parent_model_type(model_type)
        if parent_model_type is None:
            return {}
        return (await cls.upsert_with_model_type(parent_model_type, create_dict, session)).model_dump()

    @staticmethod
    def dump_create_object(create_object: CreateSchemaBaseType) -> dict[str, Any]:
        """
        Создаем словарь для схемы создания модели.
        """
        create_dict = create_object.model_dump()
        if create_dict['id'] is None:
            del create_dict['id']
        return create_dict

    @classmethod
    def get_parent_model_type(cls, model_type: type[ModelBaseType]) -> type[ModelBaseType] | None:
        """
        Получаем тип родительской модели.
        """
        if not model_type.__bases__ or model_type.__bases__[0] not in cls.model_types:
            return None
        return model_type.__bases__[0]

    @classmethod
    def check_get_by_ids_exact(cls, ids: Sequence[IdType], models: Sequence[ModelBaseType], exact: bool) -> None:
        """
        Проверяем, что по идентификаторам получены все модели.
        """
        if exact and len(ids) != len(models):
            raise ModelNotFoundError(
                cls.model_type,
                model_id=set(ids) - {cast(IdType, model.id) for model in models},
            )

    async def paginate_with_filter(
        self: Self,
        pagination: PaginationSchema,
        user: Any,
        policies: list[str],
        *,
        search: str | None = None,
        search_by: Iterable[str] | None = None,
        sorting: Iterable[str] | None = None,
        select_filter: Callable[[sa.Select[tuple[ModelBaseType]]], sa.Select[tuple[ModelBaseType]]] | None = None,
    ) -> PaginationResultSchema[ReadSchemaBaseType]:
        """
        Получаем список моделей с пагинацией, поиском, сортировкой и фильтрами.
        """
        if len(policies) == 0:
            return PaginationResultSchema(objects=[], count=0)
        search_by = search_by or []
        sorting = sorting or []
        async with self.session_manager.get_session() as s:
            statement = self.select()
            if select_filter:
                statement = select_filter(statement)
            if search:
                search_where: sa.ColumnElement[Any] = sa.false()
                for sb in search_by:
                    search_where = sa.or_(search_where, getattr(self.model_type, sb).ilike(f'%{search}%'))
                statement = statement.where(search_where)
            order_by_expr = self.get_order_by_expr(sorting)
            models = (
                (await s.execute(statement.limit(pagination.limit).offset(pagination.offset).order_by(*order_by_expr)))
                .scalars()
                .all()
            )
            objects = [self.model_validate(model) for model in models]
            count_statement = statement.with_only_columns(func.count(self.model_type.id))
            count = (await s.execute(count_statement)).scalar_one()
            return PaginationResultSchema(count=count, objects=objects)

    def get_order_by_expr(self: Self, sorting: Iterable[str]) -> list[sa.UnaryExpression]:
        """
        Получаем выражение сортировки.
        """
        order_by_expr: list[sa.UnaryExpression] = []
        for st in sorting:
            try:
                if st[0] == '-':
                    order_by_expr.append(getattr(self.model_type, st[1:]).desc())
                else:
                    order_by_expr.append(getattr(self.model_type, st))
            except AttributeError as attribute_error:
                raise SortingFieldNotFoundError(st) from attribute_error
        return order_by_expr


class DbCrudRepositoryInt(
    DbCrudRepositoryBase[
        ModelIntType,
        ReadSchemaIntType,
        CreateSchemaIntType,
        UpdateSchemaIntType,
        int,
    ],
    Generic[
        ModelIntType,
        ReadSchemaIntType,
        CreateSchemaIntType,
        UpdateSchemaIntType,
    ],
):
    """
    Репозиторий для выполнения CRUD операций над моделями старого типа в базе данных.
    """

    __abstract__ = True


class DbCrudRepository(
    DbCrudRepositoryBase[ModelType, ReadSchemaType, CreateSchemaType, UpdateSchemaType, uuid.UUID],
    Generic[ModelType, ReadSchemaType, CreateSchemaType, UpdateSchemaType],
):
    """
    Репозиторий для выполнения CRUD операций над моделями нового типа в базе данных.
    """

    __abstract__ = True
