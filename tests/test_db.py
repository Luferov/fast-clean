"""
Модуль, содержащий тесты функционала, связанного с базой данных.
"""

from typing import cast
from unittest.mock import MagicMock

import sqlalchemy as sa
from fast_clean.db import SessionManagerImpl
from pytest_mock import MockerFixture


class TestSessionManager:
    """
    Тесты менеджера сессий.
    """

    @staticmethod
    async def test_get_session_begin(session_manager: SessionManagerImpl) -> None:
        """
        Тестируем запуск транзакции в методе `begin`.
        """
        assert not session_manager.session.in_transaction()
        async with session_manager.get_session():
            assert session_manager.session.in_transaction()
        assert not session_manager.session.in_transaction()

    @staticmethod
    async def test_get_session_immediate(session_manager: SessionManagerImpl, mocker: MockerFixture) -> None:
        """
        Тестируем запуск транзакции в методе `begin` с параметром `immediate=True`.
        """
        mocker.patch.object(session_manager.session, 'execute')
        assert not session_manager.session.in_transaction()
        async with session_manager.get_session():
            assert session_manager.session.in_transaction()
        execute = cast(MagicMock, session_manager.session.execute)
        mocker.patch.object(sa.text, '__eq__', lambda self, other: str(self) == str(other))
        execute.assert_called_once()
        call_args = execute.call_args[0]
        assert len(call_args) == 1
        assert str(call_args[0]) == str(sa.text('SET CONSTRAINTS ALL IMMEDIATE'))
        assert not session_manager.session.in_transaction()
