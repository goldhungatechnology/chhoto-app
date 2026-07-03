from typing import Annotated, Literal
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.settings import config
from src.core.utils.response import (
    CustomSuccessResponseSchema,
    CustomResponse as cr,
    get_cookie_response,
)
from src.modules.auth.application.usecases.oauth.authenticate_user_oauth_usecase import (
    AuthenticatUserOAuthUseCase,
)
from src.modules.auth.application.usecases.oauth.begin_oauth_usecase import (
    BeginOAuthUseCase,
)
from src.modules.auth.auth_container import get_auth_container
from src.modules.auth.infrastructure.uow.auth_uow import AuthUOW
from src.shared.infrastructure.logger import logger
from src.shared.infrastructure.db import get_async_session

public_router = APIRouter()


## main router
router = APIRouter()
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


## ------------------------------- Public Routers --------------------------------------
@public_router.get(
    "/oauth/login/{provider}", response_model=CustomSuccessResponseSchema
)
async def oauth_login(
    request: Request, provider: Literal["google"], session: AsyncSessionDep
):
    """
    Endpoint to initiate the OAuth login flow for a given provider.
    It returns the URL to redirect the user to for authentication.
    """

    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        use_case: BeginOAuthUseCase = auth_container.begin_oauth_usecase()

        return await use_case.execute(provider=provider, request=request)


@public_router.get(
    "/oauth/callback/{provider}", response_model=CustomSuccessResponseSchema
)
async def oauth_callback(
    request: Request, provider: Literal["google"], session: AsyncSessionDep
):
    """
    Endpoint to handle the OAuth callback after the user has authenticated with the provider.
    It processes the callback, retrieves user information, and returns authentication cookies.
    """

    try:
        async with AuthUOW(session):
            auth_container = get_auth_container(session)
            use_case: AuthenticatUserOAuthUseCase = (
                auth_container.authenticate_user_oauth_usecase()
            )

            status, payload = await use_case.execute(provider=provider, request=request)

            match status:
                case "mfa":
                    # MFA is required: no session is issued. Hand the short-lived
                    # temp token to the frontend so it can complete the MFA step.
                    return cr.redirect(
                        url=(
                            f"{config.FRONTEND_URL}/mfa"
                            f"?temp_token={payload['temp_token']}"
                        )
                    )

                case "login":
                    response = cr.redirect(url=config.OAUTH_SUCCESS_REDIRECT_URL)
                    return get_cookie_response(
                        cookies={
                            "session_uuid": {"value": payload["session_uuid"]},
                        },
                        response=response,
                    )

                case "signup":
                    response = cr.redirect(url=config.OAUTH_SUCCESS_REDIRECT_URL)
                    return get_cookie_response(
                        cookies={
                            "session_uuid": {"value": payload["session_uuid"]},
                        },
                        response=response,
                    )
    except Exception as e:
        logger.exception(f"Error during OAuth callback processing: {str(e)}")
        return cr.redirect(url=config.OAUTH_FAILURE_REDIRECT_URL)


## ------------------------------- Include Routers --------------------------------------
router.include_router(public_router)
