"""
Роутер приложения healthcheck.
"""

from fastapi import APIRouter

from .schemas import StatusOkResponseSchema

router = APIRouter(prefix='/health', tags=['Healthcheck'], include_in_schema=False)


@router.get('')
async def get_healthcheck_status() -> StatusOkResponseSchema:
    """
    Получаем статус сервера.
    """
    return StatusOkResponseSchema()
