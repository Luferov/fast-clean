from fast_clean.schemas.request_response import RequestResponseSchema


class StatusOkResponseSchema(RequestResponseSchema):
    """
    Successful response schema.
    """

    status: str = 'ok'
