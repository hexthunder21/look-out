from fastapi import APIRouter
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.targets import router as targets_router

api_router = APIRouter(prefix="/v1")
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(targets_router, prefix="/targets", tags=["targets"])