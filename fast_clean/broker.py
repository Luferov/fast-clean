"""
Модуль, содержащий функционал, связанный с брокером сообщений.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import partial
from typing import Callable, Self

from faststream import ExceptionMiddleware
from faststream.kafka import KafkaBroker
from faststream.kafka.fastapi import KafkaRouter
from faststream.security import BaseSecurity, SASLPlaintext

from fast_clean.settings import CoreKafkaSettingsSchema
from fast_clean.utils import CertificateSchema, make_ssl_context


class BrokerFactory:
    """
    Фабрика брокеров сообщений.
    """

    router: KafkaRouter | None = None

    @classmethod
    def get_router(cls, kafka_settings: CoreKafkaSettingsSchema) -> KafkaRouter:
        if cls.router is None:
            cls.router = cls.make_router(kafka_settings)
        return cls.router

    @classmethod
    def make_static(cls, kafka_settings: CoreKafkaSettingsSchema) -> KafkaBroker:
        """
        Создаем брокер сообщений с помощью статического роутера.
        """
        return cls.get_router(kafka_settings).broker

    @classmethod
    @asynccontextmanager
    async def make_dynamic(cls, kafka_settings: CoreKafkaSettingsSchema) -> AsyncIterator[KafkaBroker]:
        """
        Создаем брокер сообщений с помощью динамического роутера.
        """
        async with cls.make_router(kafka_settings).broker as broker:
            yield broker

    @classmethod
    def make_router(cls, kafka_settings: CoreKafkaSettingsSchema) -> KafkaRouter:
        """
        Создаем роутер.
        """
        credentials = BrokerCredentials(kafka_settings)
        return KafkaRouter(
            kafka_settings.bootstrap_servers,
            security=credentials.get(),
            asyncapi_url='/asyncapi',
            middlewares=[cls.make_exception_middleware()],
        )

    @classmethod
    def make_exception_middleware(cls) -> ExceptionMiddleware:
        """
        Создаем middleware для обработки исключений.
        """
        exception_middleware = ExceptionMiddleware()
        exception_middleware.add_handler(Exception)(cls.exception_handler)
        return exception_middleware

    @staticmethod
    def exception_handler(exception: Exception) -> None:
        """
        Обработчик исключения.
        """
        print(repr(exception))


class BrokerCredentials:
    """
    Класс получения параметров для подключения к Kafka.
    """

    def __init__(self, kafka_settings: CoreKafkaSettingsSchema) -> None:
        self.kafka_settings = kafka_settings

    def get(self: Self, use_ssl: bool = True) -> BaseSecurity | SASLPlaintext | None:
        """
        Получаем параметры для подключения.
        """
        if self.kafka_settings.credentials is None:
            return self.get_none_credentials()

        credentials_mapping: dict[str, Callable[[], BaseSecurity | SASLPlaintext | None]] = {
            'SSL': partial(self.get_ssl_credentials, use_ssl),
            'SASL': partial(self.get_sasl_credentials, use_ssl),
        }
        return credentials_mapping.get(self.kafka_settings.credentials, self.get_none_credentials)()

    @staticmethod
    def get_none_credentials() -> None:
        """
        Получаем отсутствующие параметры для подключения.
        """
        return None

    def get_ssl_credentials(self: Self, use_ssl: bool = True) -> BaseSecurity:
        """
        Получаем SSL параметры для подключения.
        """
        ssl_context = make_ssl_context(CertificateSchema.model_validate(self.kafka_settings.model_dump()))
        return BaseSecurity(ssl_context, use_ssl)

    def get_sasl_credentials(self: Self, use_ssl: bool = True) -> SASLPlaintext:
        """
        Получаем SASL параметры для подключения.
        """
        assert self.kafka_settings.broker_username
        assert self.kafka_settings.broker_password
        return SASLPlaintext(
            username=self.kafka_settings.broker_username,
            password=self.kafka_settings.broker_password,
            use_ssl=use_ssl,
        )
