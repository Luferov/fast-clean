"""
Модуль, содержащий тесты функционала, связанного с брокером сообщений.
"""

import ssl

from fast_clean.broker import BrokerCredentials
from fast_clean.settings import CoreKafkaSettingsSchema
from faststream.security import BaseSecurity, SASLPlaintext
from pytest_mock import MockFixture

from tests.settings import SettingsSchema


class TestBrokerCredentials:
    """
    Тесты класса получения параметров для подключения к Kafka.
    """

    @staticmethod
    def test_none_credentials(settings: SettingsSchema) -> None:
        """
        Тестируем получение отсутствующих параметров для подключения.
        """
        credentials = BrokerCredentials(
            CoreKafkaSettingsSchema(
                bootstrap_servers=settings.kafka.bootstrap_servers, group_id=settings.kafka.group_id
            )
        )
        assert credentials.get() is None

    @staticmethod
    def test_ssl_credentials(settings: SettingsSchema, mocker: MockFixture) -> None:
        """
        Тестируем получение SSL параметров для подключения.
        """
        kafka_settings = CoreKafkaSettingsSchema(
            group_id=settings.kafka.group_id,
            bootstrap_servers=settings.kafka.bootstrap_servers,
            credentials='SSL',
            ca_file='path/to/ca.pem',
            cert_file='path/to/cert.pem',
            key_file='path/to/key.pem',
            password='test_password',
        )
        mock_create_default_context = mocker.patch('ssl.create_default_context')
        credentials = BrokerCredentials(kafka_settings)
        security = credentials.get()
        mock_create_default_context.assert_called_once_with(
            purpose=ssl.Purpose.SERVER_AUTH, cafile=kafka_settings.ca_file
        )
        mock_ssl_context = mock_create_default_context.return_value
        mock_ssl_context.load_cert_chain.assert_called_once_with(
            certfile=kafka_settings.cert_file, keyfile=kafka_settings.key_file, password=kafka_settings.password
        )
        assert isinstance(security, BaseSecurity)
        assert security.use_ssl
        ssl_context = security.ssl_context
        assert ssl_context is not None
        assert ssl_context == mock_ssl_context
        assert not ssl_context.check_hostname

    @staticmethod
    def test_sasl_credentials(settings: SettingsSchema) -> None:
        """
        Тестируем получение SASL параметров для подключения.
        """
        kafka_settings = CoreKafkaSettingsSchema(
            group_id=settings.kafka.group_id,
            bootstrap_servers=settings.kafka.bootstrap_servers,
            credentials='SASL',
            broker_username='test_user',
            broker_password='test_password',
        )
        credentials = BrokerCredentials(kafka_settings)
        security = credentials.get()
        assert isinstance(security, SASLPlaintext)
        assert security.use_ssl
        assert security.username == kafka_settings.broker_username
        assert security.password == kafka_settings.broker_password
