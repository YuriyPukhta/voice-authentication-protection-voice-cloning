from fastapi import APIRouter

from src.api.auth.route import auth_router
from src.api.base_route import base_router


api_router = APIRouter(prefix="/v1", tags=["auth"])
api_router.include_router(base_router)
api_router.include_router(auth_router)