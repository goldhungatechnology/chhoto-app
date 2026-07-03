from fastapi import APIRouter

from src.modules.visitor.presentation.routers.visitor_dashboard_routers import (
    router as visitor_dashboard_router,
)
from src.modules.visitor.presentation.routers.visitor_routers import (
    router as visitor_public_router,
)

router = APIRouter()
router.include_router(visitor_public_router, tags=["Visitor - Tracking"])
router.include_router(visitor_dashboard_router, tags=["Visitor - Analytics"])

__all__ = ["router"]
