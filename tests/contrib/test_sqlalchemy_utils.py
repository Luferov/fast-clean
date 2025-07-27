from enum import StrEnum, auto
from unittest.mock import Mock

import pytest
import sqlalchemy_utils
from alembic.autogenerate.api import AutogenContext
from fast_clean.contrib.sqlalchemy_utils.utils import render_item
from sqlalchemy import LargeBinary, String


def mock_autogen_context():
    context = Mock(spec=AutogenContext)
    context.imports = set()
    return context


class ChoicesTypeEnum(StrEnum):
    A = auto()
    B = auto()


# Тесты для ChoiceType
class TestRenderItemChoiceType:
    @pytest.fixture
    def choice_type(self):
        return sqlalchemy_utils.types.ChoiceType(choices=ChoicesTypeEnum, impl=String(50))

    def test_choice_type_render(self, choice_type):
        context = mock_autogen_context()
        result = render_item('type', choice_type, context)
        assert result == 'sqlalchemy_utils.types.ChoiceType(ChoicesTypeEnum, impl=sa.String())'
        assert context.imports == {
            'from tests.contrib.test_sqlalchemy_utils import ChoicesTypeEnum',
            'import sqlalchemy_utils',
        }

    def test_choice_type_with_custom_impl(self, choice_type):
        choice_type.impl = LargeBinary()
        context = mock_autogen_context()
        result = render_item('type', choice_type, context)
        assert result == 'sqlalchemy_utils.types.ChoiceType(ChoicesTypeEnum, impl=sa.LargeBinary())'


# Тесты для JSONType
class TestRenderItemJSONType:
    def test_json_type_render(self):
        context = mock_autogen_context()
        json_type = sqlalchemy_utils.types.JSONType()
        result = render_item('type', json_type, context)
        assert result == 'sqlalchemy_utils.types.JSONType()'
        assert context.imports == {'import sqlalchemy_utils'}


# Тесты для UUIDType
class TestRenderItemUUIDType:
    @pytest.mark.parametrize(
        'binary, expected',
        [
            (True, 'sqlalchemy_utils.types.UUIDType(binary=True)'),
            (False, 'sqlalchemy_utils.types.UUIDType(binary=False)'),
        ],
    )
    def test_uuid_type_render(self, binary, expected):
        context = mock_autogen_context()
        uuid_type = sqlalchemy_utils.types.UUIDType(binary=binary)
        result = render_item('type', uuid_type, context)
        assert result == expected
        assert context.imports == {'import sqlalchemy_utils'}


# Тесты для неподдерживаемых типов
class TestRenderItemUnsupported:
    def test_unsupported_type(self):
        context = mock_autogen_context()
        result = render_item('type', 'unsupported_object', context)
        assert result is False

    def test_unsupported_item_type(self):
        context = mock_autogen_context()
        result = render_item('table', 'some_table', context)
        assert result is False
