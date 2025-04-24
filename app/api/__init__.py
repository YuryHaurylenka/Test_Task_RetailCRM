from fastapi import APIRouter

from app.core.config import settings
from .customers import router as customers_router
from .orders import router as orders_router

api_router = APIRouter(prefix=settings.api_prefix)
api_router.include_router(customers_router)
api_router.include_router(orders_router)
