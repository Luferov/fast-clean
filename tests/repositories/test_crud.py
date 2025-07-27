"""
Модуль, содержащий тесты репозиториев CRUD операций над моделями.
"""

import uuid
from collections.abc import Hashable, Iterable
from typing import cast

import pytest
from fast_clean.exceptions import ModelIntegrityError, ModelNotFoundError
from fast_clean.schemas import PaginationSchema

from .repositories import ModelRepositoryProtocol
from .schemas import (
    CrudChildAModelCreateSchema,
    CrudChildAModelReadSchema,
    CrudChildAModelUpdateSchema,
    CrudChildBModelCreateSchema,
    CrudChildBModelReadSchema,
    CrudChildBModelUpdateSchema,
    CrudParentModelCreateSchema,
    CrudParentModelReadSchema,
    CrudParentModelUpdateSchema,
)

PARENT_MODELS = [
    CrudParentModelReadSchema(id=uuid.uuid4(), str_column=f'parent model{i}', int_column=i) for i in range(10)
]
PARENT_MODELS.append(CrudParentModelReadSchema(id=uuid.uuid4(), str_column='parent model10', int_column=9))
CHILD_A_MODELS = [
    CrudChildAModelReadSchema(id=uuid.uuid4(), str_column=f'child a model{i}', int_column=i, float_column=i / 2)
    for i in range(10)
]
CHILD_B_MODELS = [
    CrudChildBModelReadSchema(id=uuid.uuid4(), str_column=f'child b model {i}', int_column=i, bool_column=i % 2 == 0)
    for i in range(10)
]
MODELS: list[CrudParentModelReadSchema] = [*PARENT_MODELS, *CHILD_A_MODELS, *CHILD_B_MODELS]

CREATE_SCHEMAS_MAPPING: dict[type[CrudParentModelReadSchema], type[CrudParentModelCreateSchema]] = {
    CrudParentModelReadSchema: CrudParentModelCreateSchema,
    CrudChildAModelReadSchema: CrudChildAModelCreateSchema,
    CrudChildBModelReadSchema: CrudChildBModelCreateSchema,
}
UPDATE_SCHEMAS_MAPPING: dict[type[CrudParentModelReadSchema], type[CrudParentModelUpdateSchema]] = {
    CrudParentModelReadSchema: CrudParentModelUpdateSchema,
    CrudChildAModelReadSchema: CrudChildAModelUpdateSchema,
    CrudChildBModelReadSchema: CrudChildBModelUpdateSchema,
}

MODELS_TO_CREATE: list[CrudParentModelReadSchema] = [
    *(CrudParentModelReadSchema(id=uuid.uuid4(), str_column=f'new parent model{i}', int_column=i) for i in range(3)),
    *(
        CrudChildAModelReadSchema(id=uuid.uuid4(), str_column=f'new child a model{i}', int_column=i, float_column=i / 2)
        for i in range(3, 6)
    ),
    *(
        CrudChildBModelReadSchema(
            id=uuid.uuid4(), str_column=f'new child b model{i}', int_column=i, bool_column=i % 2 == 0
        )
        for i in range(6, 9)
    ),
]
MODELS_TO_UPDATE: list[tuple[CrudParentModelReadSchema, CrudParentModelReadSchema]] = [
    *(
        (
            parent_model,
            CrudParentModelReadSchema(
                id=parent_model.id, str_column=f'updated parent model{i}', int_column=parent_model.int_column
            ),
        )
        for i, parent_model in enumerate(PARENT_MODELS[:5])
    ),
    *(
        (
            child_a_model,
            CrudChildAModelReadSchema(
                id=child_a_model.id, str_column=child_a_model.str_column, int_column=i * 1000, float_column=i + 1000.5
            ),
        )
        for i, child_a_model in enumerate(CHILD_A_MODELS[:5])
    ),
    *(
        (
            child_b_model,
            CrudChildBModelReadSchema(
                id=child_b_model.id,
                str_column=f'updated child b model{i}',
                int_column=child_b_model.int_column,
                bool_column=not child_b_model.bool_column,
            ),
        )
        for i, child_b_model in enumerate(CHILD_B_MODELS[:5])
    ),
]


@pytest.mark.parametrize(
    'crud_repository',
    [('in_memory', MODELS), ('db', MODELS)],
    indirect=True,
)
class TestCrudRepositories:
    """
    Тесты репозиториев для выполнения CRUD операций над моделями.
    """

    @staticmethod
    async def test_get(crud_repository: ModelRepositoryProtocol) -> None:
        """
        Тестируем метод `get`.
        """
        for expected_model in MODELS:
            assert await crud_repository.get(expected_model.id) == expected_model

    @staticmethod
    async def test_get_or_none(crud_repository: ModelRepositoryProtocol) -> None:
        """
        Тестируем метод `get_or_none`.
        """
        for expected_model in MODELS:
            assert await crud_repository.get_or_none(expected_model.id) == expected_model
        assert await crud_repository.get_or_none(uuid.uuid4()) is None

    @staticmethod
    async def test_get_by_ids(crud_repository: ModelRepositoryProtocol) -> None:
        """
        Тестируем метод `get_by_ids`.
        """
        models = [*PARENT_MODELS[:5], *CHILD_A_MODELS[:5], *CHILD_B_MODELS[:5]]
        model_ids = [model.id for model in models]
        non_existent_ids = [uuid.uuid4(), uuid.uuid4()]
        model_ids.extend(non_existent_ids)
        assert set(await crud_repository.get_by_ids(model_ids)) == set(models)
        with pytest.raises(ModelNotFoundError) as exc_info:
            await crud_repository.get_by_ids(model_ids, exact=True)
        assert isinstance(exc_info.value.model_id, Iterable)
        assert set(exc_info.value.model_id) == set(non_existent_ids)

    @staticmethod
    async def test_get_all(crud_repository: ModelRepositoryProtocol) -> None:
        """
        Тестируем метод `get_all`.
        """
        assert set(await crud_repository.get_all()) == set(MODELS)

    @staticmethod
    async def test_paginate_sorting(crud_repository: ModelRepositoryProtocol) -> None:
        """
        Тестируем сортировку в методе `paginate`.
        """
        expected_models = sorted((model for model in MODELS), key=lambda model: (model.str_column, -model.int_column))
        pagination_result = await crud_repository.paginate(
            PaginationSchema(limit=len(MODELS), offset=0),
            sorting=['str_column', '-int_column'],
        )
        assert pagination_result.count == len(expected_models)
        assert pagination_result.objects == expected_models

    @staticmethod
    async def test_paginate_search(crud_repository: ModelRepositoryProtocol) -> None:
        """
        Тестируем поиск в методе `paginate`.
        """
        search = '6'
        expected_models = {cast(Hashable, model) for model in MODELS if search in model.str_column}
        pagination_result = await crud_repository.paginate(
            PaginationSchema(limit=10, offset=0),
            search_by=['str_column'],
            search=search,
        )
        assert pagination_result.count == len(expected_models)
        assert set(pagination_result.objects) == expected_models

    @classmethod
    async def test_create(cls, crud_repository: ModelRepositoryProtocol) -> None:
        """
        Тестируем метод `create`.
        """
        for model_to_create in MODELS_TO_CREATE:
            assert await crud_repository.get_or_none(model_to_create.id) is None
            created_model = await crud_repository.create(
                CREATE_SCHEMAS_MAPPING[type(model_to_create)].model_validate(model_to_create.model_dump())
            )
            assert created_model == model_to_create
            assert await crud_repository.get(model_to_create.id) == model_to_create
        with pytest.raises(ModelIntegrityError):
            await crud_repository.create(CrudParentModelCreateSchema.model_validate(PARENT_MODELS[0].model_dump()))

    @classmethod
    async def test_bulk_create(cls, crud_repository: ModelRepositoryProtocol) -> None:
        """
        Тестируем метод `bulk_create`.
        """
        ids_to_create = [model.id for model in MODELS_TO_CREATE]
        assert [] == await crud_repository.get_by_ids(ids_to_create)
        create_schemas = [
            CREATE_SCHEMAS_MAPPING[type(model)].model_validate(model.model_dump()) for model in MODELS_TO_CREATE
        ]
        actual_models = await crud_repository.bulk_create(create_schemas)
        assert set(actual_models) == set(MODELS_TO_CREATE)
        assert set(await crud_repository.get_by_ids(ids_to_create)) == set(MODELS_TO_CREATE)
        create_schemas.append(CrudParentModelCreateSchema.model_validate(PARENT_MODELS[0].model_dump()))
        with pytest.raises(ModelIntegrityError):
            await crud_repository.bulk_create(create_schemas)

    @classmethod
    async def test_update(cls, crud_repository: ModelRepositoryProtocol) -> None:
        """
        Тестируем метод `update`.
        """
        for original_model, expected_updated_model in MODELS_TO_UPDATE:
            actual_model = await crud_repository.get(original_model.id)
            assert actual_model == original_model
            assert actual_model != expected_updated_model
            actual_updated_model = await crud_repository.update(
                UPDATE_SCHEMAS_MAPPING[type(expected_updated_model)].model_validate(expected_updated_model.model_dump())
            )
            assert actual_updated_model == expected_updated_model
            actual_model = await crud_repository.get(original_model.id)
            assert actual_model != original_model
            assert actual_model == actual_updated_model

    @classmethod
    async def test_bulk_update(cls, crud_repository: ModelRepositoryProtocol) -> None:
        """
        Тестируем метод `bulk_update`.
        """
        ids_to_update = [models[0].id for models in MODELS_TO_UPDATE]
        original_models = [models[0] for models in MODELS_TO_UPDATE]
        expected_updated_models = [models[1] for models in MODELS_TO_UPDATE]
        actual_models = set(await crud_repository.get_by_ids(ids_to_update))
        assert actual_models == set(original_models)
        assert actual_models != set(expected_updated_models)
        await crud_repository.bulk_update(
            [
                UPDATE_SCHEMAS_MAPPING[type(model)].model_validate(model.model_dump())
                for model in expected_updated_models
            ]
        )
        actual_models = set(await crud_repository.get_by_ids(ids_to_update))
        assert actual_models == set(expected_updated_models)
        assert actual_models != set(original_models)

    @classmethod
    async def test_upsert_create(cls, crud_repository: ModelRepositoryProtocol) -> None:
        """
        Тестируем создание модели с помощью метода `upsert`.
        """
        for model_to_create in MODELS_TO_CREATE:
            assert await crud_repository.get_or_none(model_to_create.id) is None
            created_model = await crud_repository.upsert(
                CREATE_SCHEMAS_MAPPING[type(model_to_create)].model_validate(model_to_create.model_dump())
            )
            assert created_model == model_to_create
            assert await crud_repository.get(model_to_create.id) == model_to_create

    @classmethod
    async def test_upsert_update(cls, crud_repository: ModelRepositoryProtocol) -> None:
        """
        Тестируем обновление модели с помощью метода `upsert`.
        """
        for original_model, expected_updated_model in MODELS_TO_UPDATE:
            actual_model = await crud_repository.get(original_model.id)
            assert actual_model == original_model
            assert actual_model != expected_updated_model
            actual_updated_model = await crud_repository.upsert(
                CREATE_SCHEMAS_MAPPING[type(expected_updated_model)].model_validate(expected_updated_model.model_dump())
            )
            assert actual_updated_model == expected_updated_model
            actual_model = await crud_repository.get(original_model.id)
            assert actual_model != original_model
            assert actual_model == actual_updated_model

    @classmethod
    async def test_delete(cls, crud_repository: ModelRepositoryProtocol) -> None:
        """
        Тестируем метод `delete`.
        """
        bound = 15
        for model in MODELS:
            assert await crud_repository.get(model.id) == model
        await crud_repository.delete([model.id for model in MODELS[:bound]])
        for i, expected_model in enumerate(MODELS):
            actual_model = await crud_repository.get_or_none(expected_model.id)
            if i < bound:
                assert actual_model is None
            else:
                assert actual_model == expected_model
