from fastapi import APIRouter

from src.modules.links.presentation.routers.link_routers import router as link_router

router = APIRouter()

router.include_router(link_router, tags=["Links - Core"])

__all__ = ["router"]
