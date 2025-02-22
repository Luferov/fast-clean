"""
Модуль, содержащий схемы ответов статусов.
"""

from .request_response import ResponseSchema


class StatusOkResponseSchema(ResponseSchema):
    """
    Схема успешного ответа.
    """

    status: str = 'ok'
