"""
Модуль, содержащий сервис для загрузки данных из файлов.
"""

import importlib
import json
import os
from pathlib import Path
from typing import Any, cast

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import SessionManagerProtocol


class SeedService:
    """
    Реализация сервиса для загрузки данных из файлов.
    """

    def __init__(self, session_manager: SessionManagerProtocol) -> None:
        self.session_manager = session_manager

    async def load_data(self, directory: str | Path | None = None) -> None:
        """
        Загружаем данные из файлов по пути.
        """
        directory = directory if directory is not None else self.find_directory()
        directory = Path(directory) if isinstance(directory, str) else directory
        async with self.session_manager.get_session() as session:
            for file in sorted(os.listdir(directory)):
                file_path = directory / file
                with open(file_path) as f:
                    items = json.load(f)
                    for item in items:
                        await self.upsert_item(item, session)

    @staticmethod
    def find_directory() -> Path:
        """
        Ищем директорию с файлами для загрузки.
        """
        cwd = Path(os.getcwd())
        virtual_env_paths = {path.parent for path in cwd.rglob('pyvenv.cfg')}
        for path in cwd.rglob('seed'):
            if not any(path.is_relative_to(venv) for venv in virtual_env_paths):
                return path
        raise ValueError('Seed directory not found')

    @classmethod
    async def upsert_item(cls, item: Any, session: AsyncSession) -> None:
        """
        Сохраняем запись в базу данных.
        """
        model_type = cls.import_from_string(item['model'])
        primary_keys = {key.name for key in cast(Any, sa.inspect(model_type)).primary_key}
        values = {**item['fields']}
        item_id = item.get('id')
        if item_id:
            values['id'] = item_id
        await session.execute(
            insert(model_type)
            .values(values)
            .on_conflict_do_update(
                index_elements=primary_keys,
                set_={k: v for k, v in values.items() if k not in primary_keys},
            )
        )

    @staticmethod
    def import_from_string(import_str: str) -> sa.TableClause:
        """
        Импортируем таблицу.
        """
        package_name, model_name = import_str.rsplit('.', maxsplit=1)
        package = importlib.import_module(package_name)
        return getattr(package, model_name)
