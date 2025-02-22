"""
Модуль, содержащий тесты создания SSL контекста.
"""

import ssl

import pytest
from fast_clean.utils.ssl_context import CertificateSchema, make_ssl_context
from pytest_mock import MockFixture


@pytest.mark.parametrize(
    'check_hostname',
    [True, False],
)
def test_make_ssl_context(mocker: MockFixture, check_hostname: bool) -> None:
    """
    Тестируем функцию `make_ssl_context`.
    """
    params = CertificateSchema(
        ca_file='path/to/ca.pem',
        cert_file='path/to/cert.pem',
        key_file='path/to/key.pem',
        password='test_password',
    )
    mock_create_default_context = mocker.patch('ssl.create_default_context')
    mock_ssl_context = mock_create_default_context.return_value
    ssl_context = make_ssl_context(params, check_hostname)
    mock_create_default_context.assert_called_once_with(purpose=ssl.Purpose.SERVER_AUTH, cafile=params.ca_file)
    mock_ssl_context.load_cert_chain.assert_called_once_with(
        certfile=params.cert_file, keyfile=params.key_file, password=params.password
    )
    assert ssl_context == mock_ssl_context
    assert ssl_context.check_hostname is check_hostname
