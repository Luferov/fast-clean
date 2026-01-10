from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics


def use_monitoring(app: FastAPI, *, app_name: str) -> None:
    app.add_middleware(
        PrometheusMiddleware,
        group_paths=True,
        filter_unhandled_paths=True,
        skip_paths=['/metrics', '/health', '/docs'],
        app_name=app_name,
    )
    app.add_route('/metrics', handle_metrics, name='metrics')
