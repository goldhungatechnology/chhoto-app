from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED

from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema
from src.modules.organization.application.usecases.core.get_organization_details_usecase import (
    GetOrganizationDetailsUseCase,
)
from src.modules.organization.application.usecases.core.list_organization_members_usecase import (
    ListOrganizationMembersUseCase,
)
from src.modules.organization.infrastructure.uow.organization_uow import OrganizationUOW
from src.modules.organization.organization_container import get_organization_container
from src.modules.organization.presentation.schemas.organization_media_schemas import (
    OrganizationMediaResponseSchema,
)
from src.modules.organization.presentation.schemas.organization_schemas import (
    CreateOrganizationRequestSchema,
    CurrentOrganizationDetailsResponseSchema,
    EditOrganizationRequestSchema,
    OrganizationMemberListResponseSchema,
    OrganizationMemberResponseSchema,
    OrganizationMemberUserSchema,
)
from src.modules.auth.infrastructure.cache.auth_cache_service import AuthCacheService
from src.shared.dependencies.access_guard import require_access
from src.shared.exceptions.base_exceptions import ForbiddenError
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

private_router = APIRouter(
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
@protected_router.post("/", response_model=CustomSuccessResponseSchema)
async def create_organization(
    request: Request, body: CreateOrganizationRequestSchema, session: AsyncSessionDep
):
    """
    Endpoint for creating organization and initial owner membership.
    """

    async with OrganizationUOW(session):
        organization_container = get_organization_container(session)
        create_organization_usecase = (
            organization_container.create_organization_usecase()
        )
        payload = await create_organization_usecase.execute(
            payload=body, actor_id=request.state.user_id
        )

    return cr.success(
        data=payload,
        message="Organization created successfully",
        status_code=HTTP_201_CREATED,
    )


## ------------------------------------------------ Private Endpoints ------------------------------------------------ ##


@private_router.get("/current", response_model=CustomSuccessResponseSchema)
async def get_organization_details(request: Request, session: AsyncSessionDep):
    """
    get current organization details
    """

    async with OrganizationUOW(session):
        organization_container = get_organization_container(session)
        usecase: GetOrganizationDetailsUseCase = (
            organization_container.get_organization_details_usecase()
        )
        organization, media = await usecase.execute(
            organization_id=request.state.organization_id
        )
        payload = {
            "organization": {
                **CurrentOrganizationDetailsResponseSchema.model_validate(
                    organization
                ).model_dump(exclude={"media"}),
                "media": (
                    OrganizationMediaResponseSchema.model_validate(media).model_dump()
                    if media
                    else None
                ),
            }
        }

    return cr.success(
        data=payload,
        message="User organizations retrieved successfully",
    )


@private_router.post("/switch", response_model=CustomSuccessResponseSchema)
async def switch_organization(
    request: Request,
    organization_uuid: str,
    session: AsyncSessionDep,
):
    """
    Endpoint for switching the user's current organization.
    """

    async with OrganizationUOW(session):
        organization_container = get_organization_container(session)
        switch_organization_usecase = (
            organization_container.switch_organization_usecase()
        )
        organization = await switch_organization_usecase.execute(
            user_id=request.state.user_id,
            target_organization_uuid=organization_uuid,
            current_session_uuid=request.state.session_uuid,
        )
        payload = {
            "current_organization": CurrentOrganizationDetailsResponseSchema.model_validate(
                organization
            ).model_dump()
        }

    return cr.success(
        data=payload,
        message="Organization switched successfully",
    )


@private_router.patch(
    "/{organization_uuid:str}", response_model=CustomSuccessResponseSchema
)
async def edit_organization(
    request: Request,
    organization_uuid: str,
    body: EditOrganizationRequestSchema,
    session: AsyncSessionDep,
):
    """
    Endpoint for editing organization details.
    """

    # The caller was authorized (via the X-Organization-Id header) for
    # request.state.organization_uuid. Reject attempts to edit a *different*
    # organization named in the path.
    if organization_uuid != getattr(request.state, "organization_uuid", None):
        raise ForbiddenError(
            error="You do not have access to this organization",
            errors={"code": "USER_NO_ORG_ACCESS"},
        )

    async with OrganizationUOW(session):
        organization_container = get_organization_container(session)
        edit_organization_usecase = organization_container.edit_organization_usecase()
        organization, media = await edit_organization_usecase.execute(
            payload=body,
            actor_id=request.state.user_id,
            organization_uuid=organization_uuid,
        )

        payload = {
            "current_organization": {
                **CurrentOrganizationDetailsResponseSchema.model_validate(
                    organization
                ).model_dump(exclude={"media"}),
                "media": (
                    OrganizationMediaResponseSchema.model_validate(media).model_dump()
                    if media
                    else None
                ),
            }
        }

    return cr.success(
        data=payload,
        message="Organization details updated successfully",
    )


@private_router.get(
    "/members",
    response_model=CustomSuccessResponseSchema[OrganizationMemberListResponseSchema],
)
async def list_organization_members(
    request: Request,
    session: AsyncSessionDep,
    member_status: Annotated[str | None, Query(alias="status")] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """
    List members of the current organization. Optional `status` filter
    (e.g. `active`). Returns paginated rows enriched with the underlying
    user's profile.
    """
    async with OrganizationUOW(session):
        container = get_organization_container(session)
        usecase: ListOrganizationMembersUseCase = (
            container.list_organization_members_usecase()
        )

        members, total, users_by_id, roles_by_member_id = await usecase.execute(
            organization_id=request.state.organization_id,
            status=member_status,
            limit=limit,
            offset=offset,
        )

        cache_service = AuthCacheService()
        user_ids = [uid for uid in users_by_id if uid is not None]
        online_by_user_id = await cache_service.are_users_online(user_ids)

        items = []
        for member in members:
            user = users_by_id.get(member.user_id)
            user_schema = None
            if user:
                user_schema = OrganizationMemberUserSchema(
                    uuid=user.uuid,
                    email=user.email,
                    avatar_bg=user.avatar_bg,
                    full_name=user.full_name,
                    avatar=user.avatar,
                    is_online=online_by_user_id.get(user.id, False),
                )
            items.append(
                OrganizationMemberResponseSchema(
                    uuid=member.uuid,
                    status=member.status,
                    joined_at=member.created_at,
                    role=(
                        roles_by_member_id.get(member.id)
                        if member.id is not None
                        else None
                    ),
                    user=user_schema,
                )
            )

        return cr.success(
            data=OrganizationMemberListResponseSchema(
                items=items,
                total=total,
                limit=limit,
                offset=offset,
            ).model_dump(),
            message="Organization members listed successfully",
        )


## ------------------------------------------------  Include Routers ------------------------------------------------ ##
router.include_router(
    protected_router,
)
router.include_router(
    private_router,
)
