"""
Модуль, содержащий сервис транзакций.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession


class TransactionService:
    """
    Реализация сервиса транзакций.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @asynccontextmanager
    async def begin(self, immediate: bool = True) -> AsyncIterator[None]:
        """
        Начинаем транзакцию.
        """
        async with self.session.begin():
            if immediate:
                await self.session.execute(sa.text('SET CONSTRAINTS ALL IMMEDIATE'))
            yield
