from fastapi import APIRouter

from src.modules.auth.presentation.routers.auth_email_routers import (
    router as auth_email_router,
)
from src.modules.auth.presentation.routers.auth_interface_setup_routers import (
    router as auth_interface_setup_router,
)
from src.modules.auth.presentation.routers.auth_mfa_routers import (
    router as auth_mfa_router,
)
from src.modules.auth.presentation.routers.auth_onboarding_routers import (
    router as auth_onboarding_router,
)
from src.modules.auth.presentation.routers.auth_password_routers import (
    router as auth_password_router,
)
from src.modules.auth.presentation.routers.auth_routers import router as auth_router
from src.modules.auth.presentation.routers.auth_session_routers import (
    router as auth_session_router,
)
from src.modules.auth.presentation.routers.auth_oauth_routers import (
    router as auth_oauth_router,
)

router = APIRouter()

router.include_router(auth_router, tags=["Authentication - Core"])
router.include_router(auth_oauth_router, tags=["Authentication - OAuth"])
router.include_router(auth_onboarding_router, tags=["Authentication - Onboarding"])
router.include_router(auth_email_router, tags=["Authentication - Email"])
router.include_router(auth_password_router, tags=["Authentication - Password"])
router.include_router(auth_mfa_router, tags=["Authentication - MFA"])
router.include_router(auth_session_router, tags=["Authentication - Session Management"])
router.include_router(
    auth_interface_setup_router, tags=["Authentication - Interface Setup"]
)

__all__ = ["router"]
