from src.modules.auth.domain.ports.user.user_reader import UserReader
from src.modules.organization.domain.ports.organization_member.organization_member_reader import (
    OrganizationMemberReader,
)
from src.modules.workforce.domain.services.team.team_domain_service import (
    TeamDomainService,
)
from src.modules.workforce.domain.services.team.team_member_domain_service import (
    TeamMemberDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class ListTeamMembersUseCase:
    """
    Use case for listing all members of a team along with the user details of
    both the member themselves and the user who added them.
    """

    def __init__(
        self,
        team_domain_service: TeamDomainService,
        team_member_domain_service: TeamMemberDomainService,
        organization_member_reader: OrganizationMemberReader,
        user_reader: UserReader,
    ):
        self.team_domain_service = team_domain_service
        self.team_member_domain_service = team_member_domain_service
        self.organization_member_reader = organization_member_reader
        self.user_reader = user_reader

    async def execute(
        self,
        *,
        team_uuid: str,
        organization_id: int,
        role: str | None = None,
        status: str | None = None,
        search: str | None = None,
        cursor: str | None = None,
        limit: int = 20,
        direction: str = "forward",
    ):
        """
        Lists members of a team with cursor-based pagination and optional
        filtering by role, organisation-member status, and text search.

        Returns:
            members:                 list of TeamMemberEntity
            member_user_by_member_id: { member_id -> UserEntity }
            users_by_id:             { user_id -> UserEntity }
            prev_cursor:             str | None
            next_cursor:             str | None
            has_previous_page:       bool
            has_next_page:           bool
        """
        try:
            team = await self.team_domain_service.get_team_by_uuid(team_uuid)
            if not team.id:
                raise ServerError(error="Team not found")

            cursor_int: int | None = None
            if cursor is not None:
                cursor_int = int(cursor)

            (
                members,
                prev_cursor,
                next_cursor,
                has_previous_page,
                has_next_page,
            ) = await self.team_member_domain_service.list_members_paginated(
                organization_id=organization_id,
                team_id=team.id,
                role=role,
                status=status,
                search=search,
                cursor=cursor_int,
                limit=limit,
                direction=direction,
            )

            org_member_ids = [m.member_id for m in members]
            org_members = await self.organization_member_reader.get_members_by_ids(
                org_member_ids
            )

            user_ids: set[int] = {om.user_id for om in org_members}
            user_ids.update(
                m.created_by_id for m in members if m.created_by_id is not None
            )

            users = await self.user_reader.get_users_by_ids(list(user_ids))
            users_by_id = {u.id: u for u in users}

            org_member_user_id_by_member_id = {om.id: om.user_id for om in org_members}
            member_user_by_member_id = {
                member_id: users_by_id.get(user_id)
                for member_id, user_id in org_member_user_id_by_member_id.items()
            }

            total_members_in_team = (
                await self.team_member_domain_service.list_team_members(team.id)
            )

            return (
                team,
                members,
                len(total_members_in_team),
                member_user_by_member_id,
                users_by_id,
                prev_cursor,
                next_cursor,
                has_previous_page,
                has_next_page,
            )
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to list team members", internal_details=str(e)
            ) from e
