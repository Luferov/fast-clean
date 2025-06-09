"""
Модуль, содержащий тесты сервиса транзакций.
"""

from fast_clean.services.transaction import TransactionService


class TestTransactionService:
    """
    Тесты сервиса транзакций.
    """

    @staticmethod
    async def test_begin(transaction_service: TransactionService) -> None:
        """
        Тестируем метод `begin`.
        """
        assert not transaction_service.session.in_transaction()
        async with transaction_service.begin():
            assert transaction_service.session.in_transaction()
        assert not transaction_service.session.in_transaction()
