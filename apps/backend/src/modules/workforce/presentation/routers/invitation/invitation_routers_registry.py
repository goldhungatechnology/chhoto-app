from fastapi import APIRouter

from src.modules.workforce.presentation.routers.invitation.invitation_routers import (
    router as invitation_router,
)

router = APIRouter()

router.include_router(invitation_router, tags=["Workforce - Invitations"])


__all__ = ["router"]
