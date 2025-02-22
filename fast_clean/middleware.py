"""
Модуль, содержащий middleware.
"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


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
    return app
