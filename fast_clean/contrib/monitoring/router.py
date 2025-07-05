from aioprometheus.asgi.starlette import metrics
from fastapi import APIRouter

router = APIRouter(tags=['Monitoring'])

router.get('/metrics')(metrics)
