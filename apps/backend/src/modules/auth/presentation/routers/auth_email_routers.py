from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema
from src.modules.auth.application.usecases.email.email_verificiation_resend_usecase import (
    EmailVerificationResendUseCase,
)
from src.modules.auth.auth_container import get_auth_container
from src.modules.auth.infrastructure.uow.auth_uow import AuthUOW
from src.modules.auth.presentation.schemas.auth_email_schemas import (
    EmailVerificationRequestSchema,
)
from src.shared.dependencies.access_guard import require_access
from src.shared.infrastructure.db import get_async_session

## Protected router for endpoints that require authentication and email verification
protected_router = APIRouter()

## main router
router = APIRouter(
    dependencies=[
        Depends(
            require_access(
                authenticated=True,
            )
        )
    ]
)
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@protected_router.post("/email/verify", response_model=CustomSuccessResponseSchema)
async def verify_email(
    request: Request, body: EmailVerificationRequestSchema, session: AsyncSessionDep
):
    """
    Endpoint for email verification.
    It verifies the user's email based on the token sent to the user's email.
    """
    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        email_verification_usecase = auth_container.email_verification_usecase()
        await email_verification_usecase.execute(
            user_id=request.state.user_id, token=body.token
        )

    return cr.success(message="Email verified successfully")


@protected_router.post("/email/resend", response_model=CustomSuccessResponseSchema)
async def resend_verification_email(request: Request, session: AsyncSessionDep):
    """
    Endpoint for resending the email verification token.
    It resends the email verification token to the user's email.
    """
    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        resend_email_verification_usecase: EmailVerificationResendUseCase = (
            auth_container.email_verification_resend_usecase()
        )
        await resend_email_verification_usecase.execute(user_id=request.state.user_id)

    return cr.success(message="Verification email resent successfully")


## ------------------------------------------------ Include routers ------------------------------------------------ ##
router.include_router(protected_router)
