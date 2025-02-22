"""
Модуль, содержащий тесты сервиса для загрузки данных из файлов.
"""

import uuid

import sqlalchemy as sa
from fast_clean.db import make_async_session_factory
from fast_clean.services.seed import SeedServiceProtocol
from sqlalchemy.orm import selectinload

from tests.settings import SettingsSchema

from .models import SeedParentModel
from .schemas import ChildModelSchema, ParentModelSchema


class TestSeedService:
    """
    Тесты сервиса для загрузки данных из файлов.
    """

    EXPECTED_MODELS = [
        ParentModelSchema(
            id=uuid.UUID('81dbc51b-59a8-4f14-ad89-0d5db95df063'),
            str_column='parent_model0',
            int_column=0,
            children=[],
        ),
        ParentModelSchema(
            id=uuid.UUID('8b32108a-42bb-4a46-9113-4b4fab87ee4d'),
            str_column='parent_model1',
            int_column=1,
            children=[
                ChildModelSchema(
                    id=uuid.UUID('20e21c15-ae54-4b00-bb1f-405dc96bde7e'),
                    str_column='child_model0',
                    int_column=3,
                    parent_id=uuid.UUID('8b32108a-42bb-4a46-9113-4b4fab87ee4d'),
                )
            ],
        ),
        ParentModelSchema(
            id=uuid.UUID('ea92844d-ee93-4708-a759-d5278acadbe9'),
            str_column='parent_model2',
            int_column=2,
            children=[
                ChildModelSchema(
                    id=uuid.UUID('d0dc2ed5-5a97-40f1-8baf-66a49ed22051'),
                    str_column='child_model1',
                    int_column=4,
                    parent_id=uuid.UUID('ea92844d-ee93-4708-a759-d5278acadbe9'),
                ),
                ChildModelSchema(
                    id=uuid.UUID('a9989714-141e-4da3-8065-2accb17438e8'),
                    str_column='child_model2',
                    int_column=5,
                    parent_id=uuid.UUID('ea92844d-ee93-4708-a759-d5278acadbe9'),
                ),
            ],
        ),
    ]

    @classmethod
    async def test_load_data_with_path_and_update(
        cls, settings: SettingsSchema, seed_service: SeedServiceProtocol
    ) -> None:
        """
        Тестируем метод `load_data` с передачей пути и обновлением созданных моделей.
        """
        path = settings.base_dir / 'data' / 'seed'
        await seed_service.load_data(path)
        assert await cls.get_actual_models(settings) == cls.EXPECTED_MODELS
        await cls.change_models(settings)
        assert await cls.get_actual_models(settings) != cls.EXPECTED_MODELS
        await seed_service.load_data(path)
        assert await cls.get_actual_models(settings) == cls.EXPECTED_MODELS

    @classmethod
    async def test_load_data_without_path(cls, settings: SettingsSchema, seed_service: SeedServiceProtocol) -> None:
        """
        Тестируем метод `load_data` с автоматическим поиском пути.
        """
        await seed_service.load_data()
        assert await cls.get_actual_models(settings) == cls.EXPECTED_MODELS

    @staticmethod
    async def get_actual_models(settings: SettingsSchema) -> list[ParentModelSchema]:
        """
        Получаем созданные модели.
        """
        async with make_async_session_factory(settings.db.dsn)() as session:
            statement = (
                sa.select(SeedParentModel)
                .order_by(SeedParentModel.int_column)
                .options(selectinload(SeedParentModel.children))
            )
            db_models = (await session.execute(statement)).scalars().all()
            for model in db_models:
                model.children = sorted(model.children, key=lambda cm: cm.int_column)
            return [ParentModelSchema.model_validate(model, from_attributes=True) for model in db_models]

    @classmethod
    async def change_models(cls, settings: SettingsSchema) -> None:
        """
        Вносим изменения в созданные модели.
        """
        async with make_async_session_factory(settings.db.dsn)() as session, session.begin():
            delete_statement = sa.delete(SeedParentModel).where(SeedParentModel.id == cls.EXPECTED_MODELS[0].id)
            await session.execute(delete_statement)
            update_statement = sa.update(SeedParentModel).values(int_column=SeedParentModel.int_column + 1)
            await session.execute(update_statement)
