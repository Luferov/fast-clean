"""
Module containing tests for the transaction service.
"""

from fast_clean.services.transaction import TransactionService


class TestTransactionService:
    """
    Tests for the transaction service.
    """

    @staticmethod
    async def test_begin(transaction_service: TransactionService) -> None:
        """
        Test the `begin` method.
        """
        assert not transaction_service.session.in_transaction()
        async with transaction_service.begin():
            assert transaction_service.session.in_transaction()
        assert not transaction_service.session.in_transaction()
