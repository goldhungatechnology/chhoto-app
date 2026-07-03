from fastapi import APIRouter

from src.modules.motivation.presentation.routers.motivation_routers import (
    router as motivation_router,
)

router = APIRouter()
router.include_router(motivation_router, tags=["Motivation - Core"])

__all__ = ["router"]
