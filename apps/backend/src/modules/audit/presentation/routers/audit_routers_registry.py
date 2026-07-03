from fastapi import APIRouter

from src.modules.audit.presentation.routers.audit_routers import router as audit_router

router = APIRouter()
router.include_router(audit_router, tags=["Audit - Core"])

__all__ = ["router"]
