from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED

from src.core.config.settings import config
from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema, get_cookie_response
from src.modules.auth.application.usecases.core.edit_user_usecase import EditUserUseCase
from src.modules.auth.application.usecases.core.get_user_details_usecase import (
    GetUserDetailsUseCase,
)
from src.modules.auth.auth_container import get_auth_container
from src.modules.auth.infrastructure.uow.auth_uow import AuthUOW
from src.modules.auth.presentation.schemas.auth_schemas import (
    CountryDetailsResponseSchema,
    EditProfileRequestSchema,
    LoginRequestSchema,
    OrganizationDetailsResponseSchema,
    SignupRequestSchema,
    UserDetailsResponseSchema,
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
                organization_member=False,
            )
        )
    ]
)

logout_router = APIRouter(
    dependencies=[
        Depends(
            require_access(
                authenticated=True,
                email_verified=False,
                onboarded=False,
                organization_member=False,
            )
        )
    ]
)


## main router
router = APIRouter()
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]

## ------------------------------------------------ Public Endpoints ------------------------------------------------ ##


@public_router.post("/signup", response_model=CustomSuccessResponseSchema)
async def signup(request: Request, body: SignupRequestSchema, session: AsyncSessionDep):
    """
    Endpoint for user signup.
    It returns the cookies for the user to be authenticated in the frontend with session_uuid
    """

    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        create_user_usecase = auth_container.create_user_usecase()
        payload = await create_user_usecase.execute(
            payload=body, ip_address=request.state.ip_address
        )

        response = cr.success(
            message="User signed up successfully",
            status_code=HTTP_201_CREATED,
        )
        return get_cookie_response(
            cookies={
                "session_uuid": {"value": payload["session_uuid"]},
            },
            response=response,
        )


@public_router.post("/login", response_model=CustomSuccessResponseSchema)
async def login(request: Request, body: LoginRequestSchema, session: AsyncSessionDep):
    """
    Endpoint for user login.
    It returns the cookies for the user to be authenticated in the frontend with session_uuid
    """

    async with AuthUOW(session):
        ip_address = request.state.ip_address
        device = request.state.device
        browser = request.state.browser

        auth_container = get_auth_container(session)
        login_user_usecase = auth_container.login_user_usecase()
        payload = await login_user_usecase.execute(
            email=body.email,
            password=body.password,
            ip_address=ip_address,
            device=device,
            browser=browser,
            captcha_token=body.captcha_token,
        )

        if payload["mfa_required"]:
            return cr.success(message="MFA is required", data=payload)

        response = cr.success(message="User logged in successfully")
        return get_cookie_response(
            cookies={
                "session_uuid": {"value": payload["session_uuid"]},
            },
            response=response,
        )


## ------------------------------------------------ Protected Endpoints ------------------------------------------------ ##


@protected_router.get(
    "/me", response_model=CustomSuccessResponseSchema[UserDetailsResponseSchema]
)
async def me(request: Request, session: AsyncSessionDep):
    """
    Endpoint to get the current user information.
    It returns the user information based on the session_uuid cookie.
    """
    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        get_user_details_usecase: GetUserDetailsUseCase = (
            auth_container.get_user_details_usecase()
        )

        (
            user,
            onboarding_details,
            organizations,
            is_online,
            last_organization,
            country,
            user_account,
            mfa_enabled,
        ) = await get_user_details_usecase.execute(
            user_id=request.state.user_id, session_uuid=request.state.session_uuid
        )
        payload = {
            "user": {
                **UserDetailsResponseSchema.model_validate(user).model_dump(
                    exclude={"is_online", "country"}
                ),
                "is_online": is_online,
                "country": (
                    CountryDetailsResponseSchema.model_validate(country).model_dump()
                    if country
                    else None
                ),
                "onboarding_details": {
                    "theme": onboarding_details.theme,
                },
            },
            "organizations": (
                [
                    OrganizationDetailsResponseSchema.model_validate(org).model_dump()
                    for org in organizations
                ]
                if organizations
                else None
            ),
            "current_organization": (
                OrganizationDetailsResponseSchema.model_validate(
                    last_organization
                ).model_dump()
                if last_organization
                else None
            ),
            "security": {
                "last_password_changed_at": (
                    user_account.last_password_updated_at if user_account else None
                ),
                "mfa_enabled": mfa_enabled,
            },
        }

    return cr.success(message="User information retrieved successfully", data=payload)


@protected_router.patch("/profile", response_model=CustomSuccessResponseSchema)
async def edit_profile(
    request: Request, body: EditProfileRequestSchema, session: AsyncSessionDep
):
    """
    Endpoint to update the current user information.
    It returns the updated user information based on the session_uuid cookie.
    """
    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        edit_user_usecase: EditUserUseCase = auth_container.edit_user_usecase()
        user = await edit_user_usecase.execute(
            user_id=request.state.user_id, payload=body
        )
        payload = {
            "user": UserDetailsResponseSchema.model_validate(user).model_dump(),
        }

        return cr.success(message="User information updated successfully", data=payload)


## ------------------------------------------------ Logout Endpoint ------------------------------------------------ ##
@logout_router.post("/logout", response_model=CustomSuccessResponseSchema)
async def logout(request: Request, session: AsyncSessionDep):
    """
    Endpoint for user logout.
    It clears the session_uuid cookie to log the user out in the frontend.
    """

    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        logout_user_usecase = auth_container.logout_user_usecase()
        await logout_user_usecase.execute(session_uuid=request.state.session_uuid)

    response = cr.success(message="User logged out successfully")

    if config.is_local or config.is_testing or config.is_development:
        response.delete_cookie(key="session_uuid")
    elif config.is_production or config.is_staging:
        response.delete_cookie(
            key="session_uuid",
            secure=True,
            httponly=True,
            samesite="none",
            domain=config.COOKIE_DOMAIN,
        )

    return response


## ------------------------------------------------ Include Routers ------------------------------------------------ ##
router.include_router(public_router)
router.include_router(protected_router)
router.include_router(logout_router)
