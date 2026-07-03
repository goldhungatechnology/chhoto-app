from fastapi import APIRouter

from src.modules.workforce.presentation.routers.team.team_routers import (
    router as team_router,
)

router = APIRouter()

router.include_router(team_router, tags=["Workforce - Teams"])


__all__ = ["router"]
