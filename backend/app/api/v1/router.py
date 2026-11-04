from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.pokja import router as pokja_router
from app.api.v1.locations import router as locations_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.documents import router as documents_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(pokja_router)
api_v1_router.include_router(locations_router)
api_v1_router.include_router(inventory_router)
api_v1_router.include_router(documents_router)

