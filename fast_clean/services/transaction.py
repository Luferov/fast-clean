"""
Module containing the transaction service.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession


class TransactionService:
    """
    Transaction service implementation.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @asynccontextmanager
    async def begin(self, immediate: bool = True) -> AsyncIterator[None]:
        """
        Start a transaction.
        """
        async with self.session.begin():
            if immediate:
                await self.session.execute(sa.text('SET CONSTRAINTS ALL IMMEDIATE'))
            yield
