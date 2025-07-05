
from fast_clean.schemas.request_response import ResponseSchema


class StatusOkResponseSchema(ResponseSchema):
    """
    Схема успешного ответа.
    """

    status: str = 'ok'
