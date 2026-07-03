from fastapi import APIRouter

from src.modules.organization.presentation.routers.organization_routers import (
    router as organization_router,
)

router = APIRouter()
router.include_router(organization_router, tags=["Organization - Core"])

__all__ = ["router"]
