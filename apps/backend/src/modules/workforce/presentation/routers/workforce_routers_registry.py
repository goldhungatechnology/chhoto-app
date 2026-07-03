from fastapi import APIRouter
from src.modules.workforce.presentation.routers.invitation.invitation_routers_registry import (
    router as invitation_router,
)
from src.modules.workforce.presentation.routers.rbac.rbac_routers_registry import (
    router as rbac_router,
)
from src.modules.workforce.presentation.routers.team.team_routers_registry import (
    router as team_router,
)

router = APIRouter()

router.include_router(rbac_router)
router.include_router(team_router)
router.include_router(invitation_router)
