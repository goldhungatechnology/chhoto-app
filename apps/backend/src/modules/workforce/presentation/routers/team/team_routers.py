from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema
from src.modules.workforce.application.usecases.team.add_team_members_usecase import (
    AddTeamMembersUseCase,
)
from src.modules.workforce.application.usecases.team.create_team_usecase import (
    CreateTeamUseCase,
)
from src.modules.workforce.application.usecases.team.delete_team_usecase import (
    DeleteTeamUseCase,
)
from src.modules.workforce.application.usecases.team.get_team_usecase import (
    GetTeamUseCase,
)
from src.modules.workforce.application.usecases.team.list_team_members_usecase import (
    ListTeamMembersUseCase,
)
from src.modules.workforce.application.usecases.team.list_teams_usecase import (
    ListTeamsUseCase,
)
from src.modules.workforce.application.usecases.team.relocate_team_members_usecase import (
    RelocateTeamMembersUseCase,
)
from src.modules.workforce.application.usecases.team.remove_team_member_usecase import (
    RemoveTeamMemberUseCase,
)
from src.modules.workforce.application.usecases.team.set_team_member_role_usecase import (
    SetTeamMemberRoleUseCase,
)
from src.modules.workforce.application.usecases.team.update_team_usecase import (
    UpdateTeamUseCase,
)
from src.modules.workforce.infrastructure.uow.workforce_uow import WorkforceUOW
from src.modules.workforce.presentation.schemas.rbac.rbac_role_schemas import (
    CreatedByUserSchema,
)
from src.modules.workforce.presentation.schemas.team.team_schemas import (
    AddTeamMembersRequestSchema,
    CreateTeamRequestSchema,
    CursorPageInfoSchema,
    RelocateTeamMembersRequestSchema,
    SetTeamMemberRoleRequestSchema,
    TeamListResponseSchema,
    TeamMemberCursorListResponseSchema,
    TeamMemberResponseSchema,
    TeamMemberSummarySchema,
    TeamResponseSchema,
    UpdateTeamRequestSchema,
)
from src.modules.auth.infrastructure.cache.auth_cache_service import AuthCacheService
from src.modules.workforce.workforce_container import get_workforce_container
from src.shared.dependencies.access_guard import require_access
from src.shared.dependencies.role_guard import require_org_role
from src.shared.infrastructure.db import get_async_session

# Privileged team-management actions require a management role, not just
# organization membership.
_MANAGER_ROLES = {"owner", "admin"}

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

router = APIRouter()
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


def _team_response(
    team, created_by_user=None, team_lead_user=None, members=None
) -> TeamResponseSchema:
    """
    Helper to convert a team entity into the response schema model.

    `members` is an optional list of (TeamMemberEntity, UserEntity | None) pairs.
    """
    created_by = (
        CreatedByUserSchema.model_validate(created_by_user) if created_by_user else None
    )
    team_lead = (
        CreatedByUserSchema.model_validate(team_lead_user) if team_lead_user else None
    )
    member_summaries = [
        TeamMemberSummarySchema(
            member_id=member.member_id,
            role=member.role,
            user=(
                CreatedByUserSchema.model_validate(member_user) if member_user else None
            ),
        )
        for member, member_user in (members or [])
    ]
    return TeamResponseSchema(
        uuid=team.uuid,
        name=team.name,
        description=team.description,
        color=team.color,
        timezone=team.timezone,
        is_default=team.is_default,
        status=team.status,
        created_at=team.created_at,
        created_by=created_by,
        team_lead=team_lead,
        members=member_summaries,
    )


def _serialize_team(
    team, created_by_user=None, team_lead_user=None, members=None
) -> dict:
    """
    Helper to convert a team entity into the response schema dict.
    """
    return _team_response(team, created_by_user, team_lead_user, members).model_dump()


def _serialize_team_member(
    member,
    member_user=None,
    added_by_user=None,
    is_online_by_user_id: dict[int, bool] | None = None,
) -> dict:
    """
    Helper to convert a team member entity into the response schema dict.
    `member_user` and `added_by_user` are optional UserEntity instances; when
    None the corresponding field on the response is left as null.
    """

    def _user_schema(user):
        is_online = (is_online_by_user_id or {}).get(user.id, False)
        return CreatedByUserSchema(
            uuid=user.uuid,
            email=user.email,
            avatar_bg=user.avatar_bg,
            full_name=user.full_name,
            avatar=user.avatar,
            is_online=is_online,
        )

    return TeamMemberResponseSchema(
        uuid=member.uuid,
        member_id=member.member_id,
        role=member.role,
        joined_at=member.created_at,
        member=_user_schema(member_user) if member_user else None,
        added_by=_user_schema(added_by_user) if added_by_user else None,
    ).model_dump()


## ----------------------------- Team Endpoints ----------------------------- ##


@protected_router.post(
    "/teams",
    response_model=CustomSuccessResponseSchema[TeamResponseSchema],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_org_role(_MANAGER_ROLES))],
)
async def create_team(
    request: Request,
    body: CreateTeamRequestSchema,
    session: AsyncSessionDep,
):
    """
    Endpoint to create a new team in the organization.
    """
    async with WorkforceUOW(session):
        container = get_workforce_container(session, request.state.organization_id)
        usecase: CreateTeamUseCase = container.create_team_usecase()

        new_team = await usecase.execute(
            organization_id=request.state.organization_id,
            name=body.name,
            description=body.description,
            color=body.color,
            timezone=body.timezone,
            is_default=False,
            actor_id=request.state.user_id,
        )

        return cr.success(
            data=_serialize_team(new_team),
            message="Team created successfully",
            status_code=status.HTTP_201_CREATED,
        )


@protected_router.get(
    "/teams",
    response_model=CustomSuccessResponseSchema[TeamListResponseSchema],
)
async def list_teams(
    request: Request,
    session: AsyncSessionDep,
    team_status: Annotated[str | None, Query(alias="status")] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """
    Endpoint to list teams in the organization. Optional `status` filter
    (e.g. `active`). Returns paginated rows.
    """
    async with WorkforceUOW(session):
        container = get_workforce_container(session, request.state.organization_id)
        usecase: ListTeamsUseCase = container.list_teams_usecase()

        (
            teams,
            total,
            users_map,
            lead_user_by_team_id,
            members_by_team_id,
        ) = await usecase.execute(
            status=team_status,
            limit=limit,
            offset=offset,
        )
        items = [
            _team_response(
                team,
                users_map.get(team.created_by_id),
                lead_user_by_team_id.get(team.id),
                members_by_team_id.get(team.id),
            )
            for team in teams
        ]

        return cr.success(
            data=TeamListResponseSchema(
                items=items,
                total=total,
                limit=limit,
                offset=offset,
            ).model_dump(),
            message="Teams listed successfully",
        )


@protected_router.get(
    "/teams/{team_uuid}",
    response_model=CustomSuccessResponseSchema[TeamResponseSchema],
)
async def get_team(
    request: Request,
    team_uuid: str,
    session: AsyncSessionDep,
):
    """
    Endpoint to retrieve a team by its UUID.
    """
    async with WorkforceUOW(session):
        container = get_workforce_container(session, request.state.organization_id)
        usecase: GetTeamUseCase = container.get_team_usecase()

        team, created_by_user = await usecase.execute(team_uuid)

        return cr.success(
            data=_serialize_team(team, created_by_user),
            message="Team retrieved successfully",
        )


@protected_router.patch(
    "/teams/{team_uuid}",
    response_model=CustomSuccessResponseSchema[TeamResponseSchema],
    dependencies=[Depends(require_org_role(_MANAGER_ROLES))],
)
async def update_team(
    request: Request,
    team_uuid: str,
    body: UpdateTeamRequestSchema,
    session: AsyncSessionDep,
):
    """
    Endpoint to update an existing team.
    """
    async with WorkforceUOW(session):
        container = get_workforce_container(session, request.state.organization_id)
        usecase: UpdateTeamUseCase = container.update_team_usecase()

        updated_team = await usecase.execute(
            team_uuid=team_uuid,
            actor_id=request.state.user_id,
            name=body.name,
            description=body.description,
            color=body.color,
            timezone=body.timezone,
            is_default=body.is_default,
        )

        return cr.success(
            data=_serialize_team(updated_team),
            message="Team updated successfully",
        )


@protected_router.delete(
    "/teams/{team_uuid}",
    response_model=CustomSuccessResponseSchema[None],
    dependencies=[Depends(require_org_role(_MANAGER_ROLES))],
)
async def delete_team(
    request: Request,
    team_uuid: str,
    session: AsyncSessionDep,
):
    """
    Endpoint to soft-delete a team.
    """
    async with WorkforceUOW(session):
        container = get_workforce_container(session, request.state.organization_id)
        usecase: DeleteTeamUseCase = container.delete_team_usecase()

        await usecase.execute(team_uuid)

        return cr.success(message="Team deleted successfully")


## ------------------------ Team Member Endpoints ------------------------ ##


@protected_router.post(
    "/teams/{team_uuid}/members",
    response_model=CustomSuccessResponseSchema[list[TeamMemberResponseSchema]],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_org_role(_MANAGER_ROLES))],
)
async def add_team_members(
    request: Request,
    team_uuid: str,
    body: AddTeamMembersRequestSchema,
    session: AsyncSessionDep,
):
    """
    Endpoint to add multiple members to a team in one request. Users are
    bucketed by role (member/supervisor/lead) as user uuids; every bucket is
    optional. Users already on the team are rejected, and assigning a lead
    enforces a single lead per team.
    """
    async with WorkforceUOW(session):
        container = get_workforce_container(session, request.state.organization_id)
        usecase: AddTeamMembersUseCase = container.add_team_members_usecase()

        members = await usecase.execute(
            team_uuid=team_uuid,
            members=body.member,
            supervisors=body.supervisor,
            lead=body.lead,
            actor_id=request.state.user_id,
        )

        return cr.success(
            data=[_serialize_team_member(member) for member in members],
            message="Team members added successfully",
            status_code=status.HTTP_201_CREATED,
        )


@protected_router.get(
    "/teams/{team_uuid}/members",
    response_model=CustomSuccessResponseSchema[TeamMemberCursorListResponseSchema],
)
async def list_team_members(
    request: Request,
    team_uuid: str,
    session: AsyncSessionDep,
    role: Annotated[str | None, Query(alias="role")] = None,
    status: Annotated[str | None, Query(alias="status")] = None,
    search: Annotated[str | None, Query(alias="search")] = None,
    cursor: Annotated[str | None, Query(alias="cursor")] = None,
    limit: int = Query(default=20, ge=1, le=100),
    direction: str = Query(default="forward", alias="direction"),
):
    """
    Endpoint to list members of a team with cursor-based pagination.
    Supports filtering by role, organisation-member status, and text search.
    """
    async with WorkforceUOW(session):
        container = get_workforce_container(session, request.state.organization_id)
        usecase: ListTeamMembersUseCase = container.list_team_members_usecase()

        (
            team,
            members,
            total_members_in_team,
            member_user_by_member_id,
            users_by_id,
            prev_cursor,
            next_cursor,
            has_previous_page,
            has_next_page,
        ) = await usecase.execute(
            team_uuid=team_uuid,
            organization_id=request.state.organization_id,
            role=role,
            status=status,
            search=search,
            cursor=cursor,
            limit=limit,
            direction=direction,
        )

        cache_service = AuthCacheService()
        all_user_ids = [uid for uid in users_by_id if uid is not None]
        online_by_user_id = await cache_service.are_users_online(all_user_ids)

        records = [
            _serialize_team_member(
                m,
                member_user=member_user_by_member_id.get(m.member_id),
                added_by_user=(
                    users_by_id.get(m.created_by_id) if m.created_by_id else None
                ),
                is_online_by_user_id=online_by_user_id,
            )
            for m in members
        ]

        return cr.success(
            data=TeamMemberCursorListResponseSchema(
                team_name=team.name,
                total_members=total_members_in_team,
                records=records,
                page_info=CursorPageInfoSchema(
                    prev_cursor=prev_cursor,
                    next_cursor=next_cursor,
                    has_previous_page=has_previous_page,
                    has_next_page=has_next_page,
                ),
            ).model_dump(),
            message="Team members listed successfully",
        )


@protected_router.delete(
    "/teams/{team_uuid}/members/{member_id}",
    response_model=CustomSuccessResponseSchema[None],
    dependencies=[Depends(require_org_role(_MANAGER_ROLES))],
)
async def remove_team_member(
    request: Request,
    team_uuid: str,
    member_id: int,
    session: AsyncSessionDep,
):
    """
    Endpoint to remove a member from a team.
    """
    async with WorkforceUOW(session):
        container = get_workforce_container(session, request.state.organization_id)
        usecase: RemoveTeamMemberUseCase = container.remove_team_member_usecase()

        await usecase.execute(team_uuid=team_uuid, member_id=member_id)

        return cr.success(message="Team member removed successfully")


@protected_router.patch(
    "/teams/{team_uuid}/members/{member_id}/role",
    response_model=CustomSuccessResponseSchema[TeamMemberResponseSchema],
    dependencies=[Depends(require_org_role(_MANAGER_ROLES))],
)
async def set_team_member_role(
    request: Request,
    team_uuid: str,
    member_id: int,
    body: SetTeamMemberRoleRequestSchema,
    session: AsyncSessionDep,
):
    """
    Endpoint to change a team member's role (member, supervisor, team lead).
    """
    async with WorkforceUOW(session):
        container = get_workforce_container(session, request.state.organization_id)
        usecase: SetTeamMemberRoleUseCase = container.set_team_member_role_usecase()

        updated = await usecase.execute(
            team_uuid=team_uuid,
            member_id=member_id,
            role=body.role,
            actor_id=request.state.user_id,
        )

        return cr.success(
            data=_serialize_team_member(updated),
            message="Team member role updated successfully",
        )


@protected_router.post(
    "/teams/{team_uuid}/members/relocate",
    response_model=CustomSuccessResponseSchema[None],
)
async def relocate_team_members(
    request: Request,
    team_uuid: str,
    body: RelocateTeamMembersRequestSchema,
    session: AsyncSessionDep,
):
    """
    Endpoint to relocate members from one team to another. This is a bulk
    operation that removes members from the specified team and adds them to
    another team. It is useful for reorganizing teams.
    """
    async with WorkforceUOW(session):
        container = get_workforce_container(session, request.state.organization_id)
        usecase: RelocateTeamMembersUseCase = container.relocate_team_members_usecase()

        await usecase.execute(
            source_team_uuid=team_uuid,
            payload=body,
        )

        return cr.success(message="Team members relocated successfully")


## ------------------------ Include Routers ------------------------ ##
router.include_router(protected_router)
