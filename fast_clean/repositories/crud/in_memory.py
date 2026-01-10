"""
Module containing the repository for CRUD operations on in-memory models.
"""

import contextlib
import uuid
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from itertools import groupby
from typing import Callable, Generic, Self, cast, get_args

from fast_clean.enums import ModelActionEnum
from fast_clean.exceptions import ModelIntegrityError, ModelNotFoundError
from fast_clean.schemas import PaginationResultSchema, PaginationSchema

from .type_vars import (
    CreateSchemaBaseType,
    CreateSchemaIntType,
    CreateSchemaType,
    IdType,
    ReadSchemaBaseType,
    ReadSchemaIntType,
    ReadSchemaType,
    UpdateSchemaBaseType,
    UpdateSchemaIntType,
    UpdateSchemaType,
)


class InMemoryCrudRepositoryBase(ABC, Generic[ReadSchemaBaseType, CreateSchemaBaseType, UpdateSchemaBaseType, IdType]):
    """
    Base repository for CRUD operations on in-memory models.
    """

    __abstract__: bool = True

    __orig_bases__: 'tuple[type[InMemoryCrudRepositoryBase[ReadSchemaBaseType, CreateSchemaBaseType, UpdateSchemaBaseType, IdType]]]'  # noqa
    __subtypes__: Sequence[tuple[type[ReadSchemaBaseType], type[CreateSchemaBaseType], type[UpdateSchemaBaseType]]]

    create_to_read_schemas_mapping: dict[type[CreateSchemaBaseType], type[ReadSchemaBaseType]]
    create_to_update_schemas_mapping: dict[type[CreateSchemaBaseType], type[UpdateSchemaBaseType]]
    update_to_read_schemas_mapping: dict[type[UpdateSchemaBaseType], type[ReadSchemaBaseType]]

    read_schema_type: type[ReadSchemaBaseType]

    def __init__(self) -> None:
        if self.__dict__.get('__abstract__', False):
            raise TypeError(f"Can't instantiate abstract class {type(self).__name__}")
        self.models: dict[IdType, ReadSchemaBaseType] = {}

    def __init_subclass__(cls) -> None:
        """
        Initialize the class.

        Get Pydantic schemas from the base class.
        """
        if cls.__dict__.get('__abstract__', False):
            return super().__init_subclass__()

        base_repository_generic = next(
            (
                base
                for base in getattr(cls, '__orig_bases__', [])
                if issubclass(getattr(base, '__origin__', base), InMemoryCrudRepositoryBase)
            ),
            None,
        )
        if not base_repository_generic:
            raise ValueError('Repository must be implemented by InMemoryCrudRepositoryBase')

        if not hasattr(cls, '__subtypes__'):
            cls.__subtypes__ = []

        cls.create_to_read_schemas_mapping = {}
        cls.create_to_update_schemas_mapping = {}
        cls.update_to_read_schemas_mapping = {}
        types: Sequence[tuple[type[ReadSchemaBaseType], type[CreateSchemaBaseType], type[UpdateSchemaBaseType]]] = [
            *cls.__subtypes__,
            get_args(base_repository_generic)[:3],
        ]
        for read_schema_type, create_schema_type, update_schema_type in types:
            cls.create_to_read_schemas_mapping[create_schema_type] = read_schema_type
            cls.create_to_update_schemas_mapping[create_schema_type] = update_schema_type
            cls.update_to_read_schemas_mapping[update_schema_type] = read_schema_type

        cls.read_schema_type, *_ = cast(
            tuple[
                type[ReadSchemaBaseType],
                type[CreateSchemaBaseType],
                type[UpdateSchemaBaseType],
            ],
            get_args(base_repository_generic),
        )
        return super().__init_subclass__()

    @abstractmethod
    def generate_id(self: Self) -> IdType:
        """
        Generate an identifier.
        """
        ...

    def get_model_name(self: Self, read_schema_type: type[ReadSchemaBaseType] | None = None) -> str:
        """
        Get the model name.
        """
        read_schema_type = read_schema_type or self.read_schema_type
        return read_schema_type.__name__.replace('Schema', '')

    async def get(self: Self, id: IdType) -> ReadSchemaBaseType:
        """
        Get a model by identifier.
        """
        model = self.models.get(id)
        if model is None:
            raise ModelNotFoundError(self.get_model_name(), model_id=id)
        return model

    async def get_or_none(self: Self, id: IdType) -> ReadSchemaBaseType | None:
        """
        Get a model or None by identifier.
        """
        with contextlib.suppress(ModelNotFoundError):
            return await self.get(id)
        return None

    async def get_by_ids(self: Self, ids: Sequence[IdType], *, exact: bool = False) -> list[ReadSchemaBaseType]:
        """
        Get a list of models by identifiers.
        """
        models: list[ReadSchemaBaseType] = []
        for id in ids:
            model = self.models.get(id)
            if model is not None:
                models.append(model)
        self.check_get_by_ids_exact(ids, models, exact)
        return models

    async def get_all(self: Self) -> list[ReadSchemaBaseType]:
        """
        Get all models.
        """
        return list(self.models.values())

    async def paginate(
        self: Self,
        pagination: PaginationSchema,
        *,
        search: str | None = None,
        search_by: Iterable[str] | None = None,
        sorting: Iterable[str] | None = None,
    ) -> PaginationResultSchema[ReadSchemaBaseType]:
        """
        Get a list of models with pagination, search, and sorting.
        """
        return self.paginate_with_filter(
            pagination,
            search=search,
            search_by=search_by,
            sorting=sorting,
        )

    async def create(self: Self, create_object: CreateSchemaBaseType) -> ReadSchemaBaseType:
        """
        Create a model.
        """
        model = self.make_model(create_object)
        self.models[cast(IdType, model.id)] = model
        return model

    async def bulk_create(self: Self, create_objects: list[CreateSchemaBaseType]) -> list[ReadSchemaBaseType]:
        """
        Create multiple models.
        """
        models: list[ReadSchemaBaseType] = []
        for create_object in create_objects:
            models.append(self.make_model(create_object))
        for model in models:
            self.models[cast(IdType, model.id)] = model
        return models

    async def update(self: Self, update_object: UpdateSchemaBaseType) -> ReadSchemaBaseType:
        """
        Update a model.
        """
        read_schema_type = self.update_to_read_schemas_mapping[type(update_object)]
        model = self.models.get(cast(IdType, update_object.id))
        if model is None:
            raise ModelNotFoundError(self.get_model_name(read_schema_type), model_id=update_object.id)
        model = cast(
            ReadSchemaBaseType,
            read_schema_type.model_validate(
                {
                    **model.model_dump(),
                    **update_object.model_dump(exclude={'id'}, exclude_unset=True),
                }
            ),
        )
        self.models[cast(IdType, model.id)] = model
        return model

    async def bulk_update(self: Self, update_objects: list[UpdateSchemaBaseType]) -> None:
        """
        Update multiple models.
        """
        for update_object in update_objects:
            await self.update(update_object)

    async def upsert(self: Self, create_object: CreateSchemaBaseType) -> ReadSchemaBaseType:
        """
        Create or update a model.
        """
        if create_object.id is None or create_object.id not in self.models:
            return await self.create(create_object)
        update_schema_type = self.create_to_update_schemas_mapping[type(create_object)]
        await self.update(
            cast(
                UpdateSchemaBaseType,
                update_schema_type.model_validate(create_object.model_dump()),
            )
        )
        return self.models[cast(IdType, create_object.id)]

    async def delete(self: Self, ids: Sequence[IdType]) -> None:
        """
        Delete models.
        """
        for id in ids:
            if id in self.models:
                del self.models[id]

    def check_get_by_ids_exact(
        self: Self,
        ids: Sequence[IdType],
        models: Sequence[ReadSchemaBaseType],
        exact: bool,
    ) -> None:
        """
        Check that all models were retrieved by identifiers.
        """
        if exact and len(ids) != len(models):
            raise ModelNotFoundError(
                self.get_model_name(),
                model_id=set(ids) - {cast(IdType, model.id) for model in models},
            )

    def paginate_with_filter(
        self: Self,
        pagination: PaginationSchema,
        *,
        search: str | None = None,
        search_by: Iterable[str] | None = None,
        sorting: Iterable[str] | None = None,
        select_filter: Callable[[ReadSchemaBaseType], bool] | None = None,
    ) -> PaginationResultSchema[ReadSchemaBaseType]:
        """
        Get a list of models with pagination, search, sorting, and filters.
        """
        search_by = search_by or []
        sorting = sorting or []
        models = list(filter(select_filter, self.models.values()) if select_filter else self.models.values())
        if search:
            search_models: list[ReadSchemaBaseType] = []
            for model in models:
                for sb in search_by:
                    if search in getattr(model, sb):
                        search_models.append(model)
            models = search_models
        models = self.sort(models, sorting)
        return PaginationResultSchema(
            objects=models[pagination.offset : pagination.offset + pagination.limit],
            count=len(models),
        )

    @classmethod
    def sort(cls, models: list[ReadSchemaBaseType], sorting: Iterable[str]) -> list[ReadSchemaBaseType]:
        """
        Sort models.
        """
        if not sorting:
            return models
        st, *sorting = sorting
        if st[0] == '-':
            sorted_models = sorted(models, key=lambda model: getattr(model, st[1:]), reverse=True)
        else:
            sorted_models = sorted(models, key=lambda model: getattr(model, st))
        result: list[ReadSchemaBaseType] = []
        for _, group_models in groupby(sorted_models, lambda model: getattr(model, st[1:] if st[0] == '-' else st)):
            result.extend(cls.sort(list(group_models), sorting))
        return result

    def make_model(self: Self, create_object: CreateSchemaBaseType) -> ReadSchemaBaseType:
        """
        Create a model without saving.
        """
        create_dict = create_object.model_dump()
        if create_dict['id'] is None:
            create_dict['id'] = self.generate_id()
        read_schema_type = self.create_to_read_schemas_mapping[type(create_object)]
        model = cast(ReadSchemaBaseType, read_schema_type.model_validate(create_dict))
        if model.id in self.models:
            raise ModelIntegrityError(self.get_model_name(read_schema_type), ModelActionEnum.INSERT)
        return model


class InMemoryCrudRepositoryInt(
    InMemoryCrudRepositoryBase[
        ReadSchemaIntType,
        CreateSchemaIntType,
        UpdateSchemaIntType,
        int,
    ],
    Generic[
        ReadSchemaIntType,
        CreateSchemaIntType,
        UpdateSchemaIntType,
    ],
):
    """
    Repository for CRUD operations on old-type models in memory.
    """

    __abstract__ = True

    def __init__(self) -> None:
        super().__init__()
        self.ids_counter = 0

    def generate_id(self: Self) -> int:
        """
        Generate an identifier.
        """
        current_id = self.ids_counter
        self.ids_counter += 1
        return current_id


class InMemoryCrudRepository(
    InMemoryCrudRepositoryBase[
        ReadSchemaType,
        CreateSchemaType,
        UpdateSchemaType,
        uuid.UUID,
    ],
    Generic[
        ReadSchemaType,
        CreateSchemaType,
        UpdateSchemaType,
    ],
):
    """
    Repository for CRUD operations on new-type models in memory.
    """

    __abstract__ = True

    def generate_id(self: Self) -> uuid.UUID:
        """
        Generate an identifier.
        """
        return uuid.uuid4()
