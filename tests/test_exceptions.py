"""
Module containing exception tests.
"""

from .exceptions import CustomTestError


class TestBusinessLogicException:
    """
    Tests for the base business logic exception.
    """

    EXPECTED_TYPE = 'custom_test'
    EXPECTED_message = 'Test message'
    EXPECTED_PARENT_message = 'Parent message'

    @classmethod
    def test_get_schema_not_debug(cls) -> None:
        """
        Test the `get_schema` method without debug.
        """
        try:
            raise CustomTestError()
        except CustomTestError as test_error:
            schema = test_error.get_schema(False)
            assert schema.type == cls.EXPECTED_TYPE
            assert schema.message == cls.EXPECTED_message
            assert schema.traceback is None

    @classmethod
    def test_get_schema_debug(cls) -> None:
        """
        Test the `get_schema` method with debug.
        """
        try:
            raise CustomTestError() from Exception(cls.EXPECTED_PARENT_message)
        except CustomTestError as test_error:
            schema = test_error.get_schema(True)
            assert schema.type == cls.EXPECTED_TYPE
            assert schema.message == cls.EXPECTED_message
            assert schema.traceback is not None
            assert CustomTestError.__name__ in schema.traceback
            assert cls.EXPECTED_message in schema.traceback
            assert Exception.__name__ in schema.traceback
            assert cls.EXPECTED_PARENT_message in schema.traceback
