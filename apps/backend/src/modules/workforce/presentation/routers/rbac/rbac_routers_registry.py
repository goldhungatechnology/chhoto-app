from fastapi import APIRouter
from src.modules.workforce.presentation.routers.rbac.rbac_routers import (
    router as rbac_router,
)

router = APIRouter()


router.include_router(rbac_router, tags=["Workforce - RBAC"])


__all__ = ["router"]
