from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema
from src.modules.links.application.usecases.create_link_usecase import CreateLinkUseCase
from src.modules.links.application.usecases.list_links_usecase import ListLinksUseCase
from src.modules.links.application.usecases.redirect_link_usecase import (
    RedirectLinkUseCase,
)
from src.modules.links.infrastructure.uow.links_uow import LinksUOW
from src.modules.links.links_container import get_links_container
from src.modules.links.presentation.schemas.link_schemas import (
    CreateLinkRequestSchema,
    LinkResponseSchema,
)
from src.shared.dependencies.access_guard import require_access
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
