"""
Модуль, содержащий тесты исключений.
"""

from .exceptions import CustomTestError


class TestBusinessLogicException:
    """
    Тесты базового исключения бизнес-логики.
    """

    EXPECTED_TYPE = 'custom_test'
    EXPECTED_MSG = 'Тестовое сообщение'
    EXPECTED_PARENT_MSG = 'Родительское сообщение'

    @classmethod
    def test_get_schema_not_debug(cls) -> None:
        """
        Тестируем метод `get_schema` без отладки.
        """
        try:
            raise CustomTestError()
        except CustomTestError as test_error:
            schema = test_error.get_schema(False)
            assert schema.type == cls.EXPECTED_TYPE
            assert schema.msg == cls.EXPECTED_MSG
            assert schema.traceback is None

    @classmethod
    def test_get_schema_debug(cls) -> None:
        """
        Тестируем метод `get_schema` с отладкой.
        """
        try:
            raise CustomTestError() from Exception(cls.EXPECTED_PARENT_MSG)
        except CustomTestError as test_error:
            schema = test_error.get_schema(True)
            assert schema.type == cls.EXPECTED_TYPE
            assert schema.msg == cls.EXPECTED_MSG
            assert schema.traceback is not None
            assert CustomTestError.__name__ in schema.traceback
            assert cls.EXPECTED_MSG in schema.traceback
            assert Exception.__name__ in schema.traceback
            assert cls.EXPECTED_PARENT_MSG in schema.traceback
