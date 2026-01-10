"""
Module containing logging-related functionality.
"""

import logging.config
import sys

import structlog

from fast_clean.settings import CoreSettingsSchema


def use_logging(settings: CoreSettingsSchema) -> None:
    shared_processors = get_shared_processors()
    render_processors = get_render_processors(settings)

    configure_structlog(shared_processors)
    configure_logging(shared_processors, render_processors)


def get_shared_processors() -> list[structlog.typing.Processor]:
    return [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.MODULE,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ],
        ),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        structlog.processors.EventRenamer('message'),
    ]


def get_render_processors(settings: CoreSettingsSchema) -> list[structlog.typing.Processor]:
    if settings.environment == 'dev':
        return [
            structlog.dev.ConsoleRenderer(),
        ]

    return [
        # Do not show variables to avoid leaking potentially sensitive data in logs.
        structlog.processors.ExceptionRenderer(structlog.tracebacks.ExceptionDictTransformer(show_locals=False)),
        structlog.processors.JSONRenderer(ensure_ascii=False),
    ]


def configure_structlog(shared_processors: list[structlog.typing.Processor]) -> None:
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def configure_logging(
    shared_processors: list[structlog.typing.Processor],
    render_processors: list[structlog.typing.Processor],
) -> None:
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'structlog': {
                '()': structlog.stdlib.ProcessorFormatter,
                'foreign_pre_chain': shared_processors,
                'processors': [
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    *render_processors,
                ],
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'structlog',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': 'INFO',
            },
        },
    }
    logging.config.dictConfig(logging_config)
