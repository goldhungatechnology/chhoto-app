from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils.response import (
    CustomSuccessResponseSchema,
    CustomResponse as cr,
    get_cookie_response,
)
from src.modules.auth.application.usecases.mfa.confirm_mfa_usecase import (
    ConfirmMFAUseCase,
)
from src.modules.auth.application.usecases.mfa.disable_mfa_usecase import (
    DisableMFAUseCase,
)
from src.modules.auth.application.usecases.mfa.setup_mfa_usecase import (
    SetupMFAUseCase,
)
from src.modules.auth.application.usecases.mfa.verify_mfa_usecase import (
    VerifyMFAUseCase,
)
from src.modules.auth.auth_container import get_auth_container
from src.modules.auth.infrastructure.uow.auth_uow import AuthUOW
from src.modules.auth.presentation.schemas.auth_mfa_schemas import (
    ConfirmMFARequestSchema,
    DisableMFARequestSchema,
    SetupMFAResponseSchema,
    VerifyMFARequestSchema,
)
from src.shared.dependencies.access_guard import require_access
from src.shared.infrastructure.db import get_async_session

protected_router = APIRouter(
    dependencies=[
        Depends(
            require_access(
                authenticated=True,
            )
        )
    ]
)

public_router = APIRouter()

router = APIRouter()
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@protected_router.post(
    "/mfa/setup",
    response_model=CustomSuccessResponseSchema[SetupMFAResponseSchema],
)
async def setup_mfa(request: Request, session: AsyncSessionDep):
    """
    Set up Multi-Factor Authentication (MFA) for the user.
    Generates a TOTP secret and provisioning URL.
    """
    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        setup_mfa_usecase: SetupMFAUseCase = auth_container.setup_mfa_usecase()
        payload = await setup_mfa_usecase.execute(
            user_id=request.state.user_id,
        )

    return cr.success(
        data=SetupMFAResponseSchema(**payload).model_dump(),
        message="MFA setup initiated successfully. Scan the QR code or enter the secret in your authenticator app.",
    )


@protected_router.post("/mfa/confirm", response_model=CustomSuccessResponseSchema)
async def confirm_mfa(
    request: Request, body: ConfirmMFARequestSchema, session: AsyncSessionDep
):
    """
    Confirm (enable) Multi-Factor Authentication by verifying the TOTP code
    from the authenticator app.
    """
    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        confirm_mfa_usecase: ConfirmMFAUseCase = auth_container.confirm_mfa_usecase()
        await confirm_mfa_usecase.execute(
            user_id=request.state.user_id,
            otp_code=body.otp_code,
        )

    return cr.success(message="MFA enabled successfully.")


@protected_router.post("/mfa/disable", response_model=CustomSuccessResponseSchema)
async def disable_mfa(
    request: Request, body: DisableMFARequestSchema, session: AsyncSessionDep
):
    """
    Disable Multi-Factor Authentication for the user.
    Requires the user's current password for confirmation.
    """
    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        disable_mfa_usecase: DisableMFAUseCase = auth_container.disable_mfa_usecase()
        await disable_mfa_usecase.execute(
            user_id=request.state.user_id,
            password=body.password,
        )

    return cr.success(message="MFA disabled successfully.")


@public_router.post("/mfa/verify", response_model=CustomSuccessResponseSchema)
async def verify_mfa(
    request: Request, body: VerifyMFARequestSchema, session: AsyncSessionDep
):
    """
    Verify the MFA code during login using the temporary token
    received from the login endpoint.
    """
    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        verify_mfa_usecase: VerifyMFAUseCase = auth_container.verify_mfa_usecase()
        payload = await verify_mfa_usecase.execute(
            temp_token=body.temp_token,
            otp_code=body.otp_code,
            ip_address=request.state.ip_address,
            device=request.state.device,
            browser=request.state.browser,
        )

    response = cr.success(message="MFA verified successfully. User logged in.")
    return get_cookie_response(
        cookies={
            "session_uuid": {"value": payload["session_uuid"]},
        },
        response=response,
    )


router.include_router(protected_router)
router.include_router(public_router)
