from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED

from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema
from src.modules.visitor.infrastructure.uow.visitor_uow import VisitorUOW
from src.modules.visitor.presentation.schemas.visitor_schemas import (
    EndSessionRequestSchema,
    HeartbeatRequestSchema,
    PageEnterRequestSchema,
    StartSessionRequestSchema,
    StartSessionResponseSchema,
    UpdateSessionRequestSchema,
)
from src.modules.visitor.visitor_container import get_visitor_container
from src.shared.dependencies.access_guard import require_access
from src.shared.infrastructure.db import get_async_session

AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]

public_router = APIRouter(
    dependencies=[
        Depends(
            require_access(
                authenticated=False,
                email_verified=False,
                onboarded=False,
                organization_member=False,
            )
        )
    ]
)

router = APIRouter()


def _client_ip(request: Request) -> str | None:
    """
    Resolve the visitor IP, honouring a proxy's X-Forwarded-For header (first
    hop) before falling back to the direct peer.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


## ----------------------------------- Public (SDK) ----------------------------------- ##
@public_router.post("/sessions/start", response_model=CustomSuccessResponseSchema)
async def start_session(
    request: Request, body: StartSessionRequestSchema, session: AsyncSessionDep
):
    """Identify the visitor and open a new browsing session."""
    async with VisitorUOW(session):
        usecase = get_visitor_container(session).start_visitor_session_usecase()
        result = await usecase.execute(
            payload=body,
            ip_address=_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )

    return cr.success(
        data=StartSessionResponseSchema(**result).model_dump(),
        message="Visitor session started",
        status_code=HTTP_201_CREATED,
    )


@public_router.post("/sessions/page-enter", response_model=CustomSuccessResponseSchema)
async def page_enter(body: PageEnterRequestSchema, session: AsyncSessionDep):
    """Record a page change within a session."""
    async with VisitorUOW(session):
        usecase = get_visitor_container(session).track_page_enter_usecase()
        result = await usecase.execute(payload=body)

    return cr.success(data=result, message="Page visit recorded")


@public_router.post("/sessions/heartbeat", response_model=CustomSuccessResponseSchema)
async def heartbeat(body: HeartbeatRequestSchema, session: AsyncSessionDep):
    """Keep the visitor's presence alive."""
    async with VisitorUOW(session):
        usecase = get_visitor_container(session).visitor_heartbeat_usecase()
        result = await usecase.execute(payload=body)

    return cr.success(data=result, message="Heartbeat accepted")


@public_router.post("/sessions/end", response_model=CustomSuccessResponseSchema)
async def end_session(body: EndSessionRequestSchema, session: AsyncSessionDep):
    """End a session (tab close / inactivity / explicit disconnect)."""
    async with VisitorUOW(session):
        usecase = get_visitor_container(session).end_visitor_session_usecase()
        result = await usecase.execute(payload=body)

    return cr.success(data=result, message="Visitor session ended")


@public_router.put(
    "/sessions/update-identity", response_model=CustomSuccessResponseSchema
)
async def update_identity(body: UpdateSessionRequestSchema, session: AsyncSessionDep):
    """Update the visitor's identity information mid-session."""
    async with VisitorUOW(session):
        usecase = get_visitor_container(session).update_visitor_identity_usecase()
        result = await usecase.execute(payload=body)

    return cr.success(data=result, message="Visitor identity updated")


router.include_router(public_router)
