from fastapi import APIRouter
from app.api.v1.endpoints.users import router as users_router

api_router = APIRouter(prefix="/v1")
api_router.include_router(users_router, prefix="/users", tags=["users"])
