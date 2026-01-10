"""
Module containing tests for database-related functionality.
"""

from typing import cast
from unittest.mock import MagicMock

import sqlalchemy as sa
from pytest_mock import MockerFixture

from fast_clean.db import SessionManagerImpl


class TestSessionManager:
    """
    Session manager tests.
    """

    @staticmethod
    async def test_get_session_begin(session_manager: SessionManagerImpl) -> None:
        """
        Test starting a transaction in the `begin` method.
        """
        assert not session_manager.session.in_transaction()
        async with session_manager.get_session():
            assert session_manager.session.in_transaction()
        assert not session_manager.session.in_transaction()

    @staticmethod
    async def test_get_session_immediate(session_manager: SessionManagerImpl, mocker: MockerFixture) -> None:
        """
        Test starting a transaction in the `begin` method with `immediate=True`.
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
