"""
Модуль, содержащий схемы запросов и ответов.
"""

from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class RequestSchema(BaseModel):
    """
    Схема запроса.
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
        )
    )


RemoteResponseSchema = RequestSchema


class ResponseSchema(BaseModel):
    """
    Схема ответа.
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        )
    )


RemoteRequestSchema = ResponseSchema
