import logging

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .enums import EnvironmentEnum


def use_sentry(
    dsn: str | None,
    environment: EnvironmentEnum = EnvironmentEnum.DEVELOPMENT,
    level: int = logging.DEBUG,
    event_level: int = logging.ERROR,
) -> None:
    sentry_logging = LoggingIntegration(
        level=level,
        event_level=event_level,
    )
    sentry_sdk.init(dsn=dsn, environment=str(environment), integrations=[sentry_logging, FastApiIntegration()])
