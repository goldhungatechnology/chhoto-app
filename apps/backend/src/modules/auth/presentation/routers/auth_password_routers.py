from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED

from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema
from src.modules.auth.application.usecases.password.forgot_password_usecase import (
    ForgotPasswordUseCase,
)
from src.modules.auth.application.usecases.password.reset_password_usecase import (
    ResetPasswordUseCase,
)
from src.modules.auth.application.usecases.password.verify_forgot_password_usecase import (
    VerifyForgotPasswordUseCase,
)
from src.modules.auth.auth_container import get_auth_container
from src.modules.auth.infrastructure.uow.auth_uow import AuthUOW
from src.modules.auth.presentation.schemas.auth_password_schemas import (
    PasswordForgotRequestSchema,
    PasswordForgotVerifyRequestSchema,
    PasswordResetRequestSchema,
)
from src.shared.dependencies.access_guard import require_access
from src.shared.infrastructure.db import get_async_session

## Define separate routers for public and protected endpoints
public_router = APIRouter()
protected_router = APIRouter(
    dependencies=[
        Depends(
            require_access(
                authenticated=True,
                email_verified=True,
                onboarded=True,
                organization_member=True,
            )
        )
    ]
)

## main router
router = APIRouter()
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


## ------------------------------------------------ Protected Endpoints ------------------------------------------------ ##
@protected_router.post("/password/reset", response_model=CustomSuccessResponseSchema)
async def reset_password(
    request: Request,
    body: PasswordResetRequestSchema,
    session: AsyncSessionDep,
):
    """
    Endpoint for changing password while authenticated.
    Verifies the old password and updates to a new one.
    Revokes all existing sessions on success.
    """

    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        reset_password_usecase: ResetPasswordUseCase = (
            auth_container.reset_password_usecase()
        )
        except_session_uuid = (
            request.state.session_uuid if body.keep_current_session else None
        )
        await reset_password_usecase.execute(
            user_id=request.state.user_id,
            old_password=body.old_password,
            new_password=body.new_password,
            except_session_uuid=except_session_uuid,
        )

    return cr.success(
        message="Password reset successfully",
        status_code=HTTP_201_CREATED,
    )


## ------------------------------------------------ Public Endpoints ------------------------------------------------ ##
@public_router.post("/password/forgot", response_model=CustomSuccessResponseSchema)
async def forgot_password(body: PasswordForgotRequestSchema, session: AsyncSessionDep):
    """
    Endpoint for forgot password.
    It resets the user's password based on the token sent to the user's email.
    """

    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        forgot_password_usecase: ForgotPasswordUseCase = (
            auth_container.forgot_password_usecase()
        )
        await forgot_password_usecase.execute(email=body.email)

    return cr.success(
        message="If the email exists, a password reset link has been sent to the email address provided.",
    )


@public_router.post(
    "/password/forgot/verify", response_model=CustomSuccessResponseSchema
)
async def verify_forgot_password(
    body: PasswordForgotVerifyRequestSchema, session: AsyncSessionDep
):
    """
    Endpoint for verifying forgot password token and resetting the password.
    It resets the user's password based on the token sent to the user's email.
    """

    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        verify_forgot_password_usecase: VerifyForgotPasswordUseCase = (
            auth_container.verify_forgot_password_usecase()
        )
        await verify_forgot_password_usecase.execute(
            token=body.token,
            new_password=body.new_password,
        )

    return cr.success(
        message="Password reset successfully",
    )


## ------------------------------------------------ Include routers ------------------------------------------------ ##

router.include_router(public_router)
router.include_router(protected_router)
