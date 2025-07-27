"""
Модуль, содержащий middleware.
"""

import time
from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.cors import CORSMiddleware


async def add_process_time_header(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    start_time = time.perf_counter()
    response = await call_next(request)
    response.headers['x-process-time'] = f'{time.perf_counter() - start_time}'
    return response


def use_middleware(
    app: FastAPI,
    name: str,
    cors_origins: list[str],
    *,
    allow_methods: list[str] | None = None,
    allow_headers: list[str] | None = None,
) -> FastAPI:
    """
    Регистрируем middleware.
    """

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=allow_methods or ['*'],
        allow_headers=allow_headers or ['*'],
    )

    app.middleware('http')(add_process_time_header)
    return app
