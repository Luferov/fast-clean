"""
Module containing helper functions for working with Pydantic.
"""

import importlib
from collections.abc import Iterable

from pydantic import BaseModel


def rebuild_schemas(modules: Iterable[str]) -> None:
    """
    Rebuild partially declared schemas due to cyclic dependencies.

    https://docs.pydantic.dev/2.10/concepts/models/#rebuilding-model-schema
    """
    schemas: dict[str, type[BaseModel]] = {}
    for module in modules:
        for key, obj in importlib.import_module(module).__dict__.items():
            if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel:
                schemas[key] = obj
    for schema in schemas.values():
        schema.model_rebuild(_types_namespace=schemas)
