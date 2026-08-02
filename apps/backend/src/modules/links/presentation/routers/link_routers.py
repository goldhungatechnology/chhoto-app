import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema
from src.modules.links.application.usecases.create_link_usecase import CreateLinkUseCase
from src.modules.links.application.usecases.list_link_sessions_usecase import (
    ListLinkSessionsUseCase,
)
from src.modules.links.application.usecases.list_links_usecase import ListLinksUseCase
from src.modules.links.application.usecases.redirect_link_usecase import (
    RedirectLinkUseCase,
)
from src.modules.links.application.usecases.update_link_usecase import UpdateLinkUseCase
from src.modules.links.infrastructure.uow.links_uow import LinksUOW
from src.modules.links.links_container import get_links_container
from src.modules.links.presentation.schemas.link_schemas import (
    CreateLinkRequestSchema,
    LinkResponseSchema,
    LinkSessionResponseSchema,
    UpdateLinkRequestSchema,
)
from src.shared.dependencies.access_guard import require_access
from src.shared.infrastructure.db import get_async_session
from src.shared.infrastructure.geoip.geoip_service import geoip_service

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

router = APIRouter()
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@protected_router.post(
    "/",
    response_model=CustomSuccessResponseSchema[LinkResponseSchema],
)
async def create_link(
    request: Request,
    body: CreateLinkRequestSchema,
    session: AsyncSessionDep,
):
    """
    Create a new short link.
    """
    async with LinksUOW(session):
        container = get_links_container(session)
        usecase: CreateLinkUseCase = container.create_link_usecase()
        link = await usecase.execute(payload=body, user_id=request.state.user_id)

    return cr.success(
        data=LinkResponseSchema.model_validate(link),
        message="Link created successfully",
    )


@protected_router.get(
    "/",
    response_model=CustomSuccessResponseSchema[list[LinkResponseSchema]],
)
async def list_links(
    request: Request,
    session: AsyncSessionDep,
):
    """
    List all links for the current user.
    """
    async with LinksUOW(session):
        container = get_links_container(session)
        usecase: ListLinksUseCase = container.list_links_usecase()
        links = await usecase.execute(user_id=request.state.user_id)

    return cr.success(
        data=[LinkResponseSchema.model_validate(link) for link in links],
        message="Links retrieved successfully",
    )


@protected_router.get(
    "/sessions/{link_uuid}",
    response_model=CustomSuccessResponseSchema[list[LinkSessionResponseSchema]],
)
async def list_link_sessions(
    link_uuid: str,
    request: Request,
    session: AsyncSessionDep,
    limit: int = 500,
):
    """
    List sessions (clicks) for a specific link by its UUID, newest first,
    bounded to the most recent ``limit`` sessions.
    """
    async with LinksUOW(session):
        container = get_links_container(session)
        usecase: ListLinkSessionsUseCase = container.list_link_sessions_usecase()
        sessions = await usecase.execute(
            link_uuid=link_uuid,
            user_id=request.state.user_id,
            limit=limit,
        )
        all_session = [
            LinkSessionResponseSchema.model_validate(s).model_dump() for s in sessions
        ]
        await asyncio.to_thread(_enrich_with_geoip, all_session)

    return cr.success(
        data=all_session,
        message="Link sessions retrieved successfully",
    )


def _enrich_with_geoip(sessions: list[dict]) -> None:
    """Populate country/city for each session. Runs in a worker thread because
    the GeoIP reader is a synchronous C-backed lookup that must not block the
    event loop."""
    for s in sessions:
        geo_data = geoip_service.lookup(ip_address=s["ip_address"])
        if not geo_data:
            s["country"] = None
            s["city"] = None
        else:
            s["country"] = geo_data.country_name
            s["city"] = geo_data.city


@protected_router.patch(
    "/{link_uuid}",
    response_model=CustomSuccessResponseSchema[LinkResponseSchema],
)
async def update_link(
    link_uuid: str,
    body: UpdateLinkRequestSchema,
    request: Request,
    session: AsyncSessionDep,
):
    """
    Update a short link title by UUID.
    """
    async with LinksUOW(session):
        container = get_links_container(session)
        usecase: UpdateLinkUseCase = container.update_link_usecase()
        link = await usecase.execute(
            link_uuid=link_uuid,
            user_id=request.state.user_id,
            title=body.title,
        )

    return cr.success(
        data=LinkResponseSchema.model_validate(link),
        message="Link updated successfully",
    )


public_router = APIRouter()


@public_router.get(
    "/redirect/{slug}",
)
async def redirect_link(
    slug: str,
    request: Request,
    session: AsyncSessionDep,
):
    """
    Resolve a short URL slug and redirect to the destination.
    Records the click and creates a link session entry.
    """
    async with LinksUOW(session):
        container = get_links_container(session)
        usecase: RedirectLinkUseCase = container.redirect_link_usecase()
        destination_url = await usecase.execute(short_url=slug, request=request)

    return cr.redirect(url=destination_url)


router.include_router(public_router)
router.include_router(protected_router)
