from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema
from src.modules.auth.application.usecases.onboarding.create_onboarding_usecase import (
    CreateOnboardingUseCase,
)
from src.modules.auth.auth_container import get_auth_container
from src.modules.auth.infrastructure.uow.auth_uow import AuthUOW
from src.modules.auth.presentation.schemas.auth_onboarding_schemas import (
    OnboardingRequestSchema,
)
from src.shared.dependencies.access_guard import require_access
from src.shared.infrastructure.db import get_async_session

protected_router = APIRouter(
    dependencies=[
        Depends(
            require_access(
                authenticated=True,
                email_verified=True,
                onboarded=False,  # Only allow users who are not onboarded
                organization_member=False,
            )
        )
    ]
)

## main router
router = APIRouter()
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


## ------------------------------------------------ Protected Endpoints ------------------------------------------------ ##
@protected_router.post("/onboarding", response_model=CustomSuccessResponseSchema)
async def onboarding(
    request: Request, body: OnboardingRequestSchema, session: AsyncSessionDep
):
    """
    Endpoint for user onboarding.
    It returns the cookies for the user to be authenticated in the frontend with session_uuid
    """
    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        create_onboarding_usecase: CreateOnboardingUseCase = (
            auth_container.create_onboarding_usecase()
        )
        _ = await create_onboarding_usecase.execute(
            payload=body, user_id=request.state.user_id
        )

    return cr.success(message="User onboarded successfully")


## ---------------------------------------------Include Routers ------------------------------------------------ ##
router.include_router(protected_router)
