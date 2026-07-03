from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from src.modules.auth.application.usecases.session.get_user_session_usecase import (
    GetUserSessionUseCase,
)
from src.modules.auth.application.usecases.session.list_all_user_session_usecase import (
    ListAllUserSessionUseCase,
)
from src.modules.auth.application.usecases.session.revoke_all_user_sessions_usecase import (
    RevokeAllUserSessionsUseCase,
)
from src.modules.auth.application.usecases.session.revoke_user_session_usecase import (
    RevokeUserSessionUseCase,
)
from src.modules.auth.presentation.schemas.auth_session_schemas import (
    CurrentSessionResponseSchema,
    RevokeAllSessionsRequestSchema,
    RevokeSessionRequestSchema,
)
from src.shared.dependencies.access_guard import require_access
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema
from src.modules.auth.auth_container import get_auth_container

from src.modules.auth.infrastructure.uow.auth_uow import AuthUOW
from src.shared.infrastructure.db import get_async_session

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

## main router
router = APIRouter()
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


def _build_session_payload(session_obj, geoip) -> dict:
    """
    Serialize a session entity and enrich it with city/country resolved from
    the session's stored IP (in-memory GeoIP lookup; None when unavailable).
    """
    geo = geoip.lookup(getattr(session_obj, "ip_address", None))
    data = CurrentSessionResponseSchema.model_validate(session_obj).model_dump(
        exclude={"expires_at", "revoked_at"}
    )
    data["city"] = geo.city if geo else None
    data["country"] = geo.country_name if geo else None
    data["country_code"] = geo.country_iso if geo else None
    return data


## ------------------------------------------------ Protected Endpoints ------------------------------------------------ ##


@protected_router.post(
    "/sessions/revoke-all", response_model=CustomSuccessResponseSchema
)
async def revoke_all_sessions(
    request: Request,
    body: RevokeAllSessionsRequestSchema,
    session: AsyncSessionDep,
):
    """
    revoke all sessions
    """
    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        usecase: RevokeAllUserSessionsUseCase = (
            auth_container.revoke_all_user_sessions_usecase()
        )
        except_session_uuid = (
            request.state.session_uuid if body.keep_current_session else None
        )
        count = await usecase.execute(
            user_id=request.state.user_id,
            except_session_uuid=except_session_uuid,
        )

    return cr.success(message=f"{count} session(s) revoked successfully")


@protected_router.post("/sessions/revoke", response_model=CustomSuccessResponseSchema)
async def revoke_session(
    request: Request,
    body: RevokeSessionRequestSchema,
    session: AsyncSessionDep,
):
    """
    revoke a single session by UUID
    """
    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        usecase: RevokeUserSessionUseCase = auth_container.revoke_user_session_usecase()
        await usecase.execute(
            session_uuid=body.session_uuid,
            user_id=request.state.user_id,
        )

    return cr.success(message="Session revoked successfully")


@protected_router.get(
    "/sessions/current",
    response_model=CustomSuccessResponseSchema[CurrentSessionResponseSchema],
)
async def get_current_session_details(
    request: Request,
    session: AsyncSessionDep,
):
    """
    get current session details
    """
    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        usecase: GetUserSessionUseCase = auth_container.get_user_session_usecase()
        session_details = await usecase.execute(session_uuid=request.state.session_uuid)
        geoip = auth_container.geoip_service()

    return cr.success(
        data=_build_session_payload(session_details, geoip),
        message="Current session details retrieved successfully",
    )


@protected_router.get(
    "/sessions",
    response_model=CustomSuccessResponseSchema[list[CurrentSessionResponseSchema]],
)
async def list_all_sessions(
    request: Request,
    session: AsyncSessionDep,
):
    """
    get all sessions for the current user
    """
    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        usecase: ListAllUserSessionUseCase = (
            auth_container.list_all_user_sessions_usecase()
        )
        sessions = await usecase.execute(user_id=request.state.user_id)
        geoip = auth_container.geoip_service()

    return cr.success(
        data=[_build_session_payload(s, geoip) for s in sessions],
        message="All sessions retrieved successfully",
    )


## ------------------------------------------------ Include Routers ------------------------------------------------ ##
router.include_router(protected_router)
