from fastapi.routing import APIRouter
from bs_custom_model_service.web.api import monitoring, data

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(data.router)
