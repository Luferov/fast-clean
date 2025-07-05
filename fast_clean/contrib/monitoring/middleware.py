from aioprometheus.asgi.middleware import MetricsMiddleware
from fastapi import FastAPI


def use_middleware(app: FastAPI) -> None:
    app.add_middleware(MetricsMiddleware)   # type: ignore
