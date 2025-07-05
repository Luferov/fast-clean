"""
Модуль, содержащий middleware.
"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .contrib.monitoring.middleware import use_middleware as use_monitoring_middleware


def use_middleware(app: FastAPI, cors_origins: list[str]) -> FastAPI:
    """
    Регистрируем middleware.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    use_monitoring_middleware(app)
    return app
