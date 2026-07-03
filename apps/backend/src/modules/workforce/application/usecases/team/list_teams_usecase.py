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


class ListTeamsUseCase:
    """
    Use case for listing teams within the current organization, enriched with
    the creator, the team members, and the team leader's user details.
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
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        """
        Executes the use case to list teams in a paginated manner.

        Returns (teams, total, users_map, lead_user_by_team_id, members_by_team_id):
            users_map:            { user_id -> UserEntity }
            lead_user_by_team_id: { team_id -> lead UserEntity }
            members_by_team_id:   { team_id -> [(TeamMemberEntity, UserEntity | None)] }
        """
        try:
            teams, total = await self.team_domain_service.list_teams_by_organization_id(
                status=status,
                limit=limit,
                offset=offset,
            )

            team_ids = [team.id for team in teams if team.id is not None]
            members = await self.team_member_domain_service.list_members_by_team_ids(
                team_ids
            )

            # Resolve each membership to its underlying user:
            # team_member.member_id -> org_member.user_id -> UserEntity.
            org_member_ids = list({m.member_id for m in members})
            org_members = await self.organization_member_reader.get_members_by_ids(
                org_member_ids
            )
            user_id_by_member_id = {om.id: om.user_id for om in org_members}

            creator_ids = {
                team.created_by_id for team in teams if team.created_by_id is not None
            }
            member_user_ids = {
                uid for uid in user_id_by_member_id.values() if uid is not None
            }
            users = await self.user_reader.get_users_by_ids(
                list(creator_ids | member_user_ids)
            )
            users_map = {user.id: user for user in users}

            # Group members per team (already ordered by membership id ascending)
            # and pair each with its resolved user.
            members_by_team_id: dict = {}
            lead_user_by_team_id: dict = {}
            for member in members:
                user = users_map.get(user_id_by_member_id.get(member.member_id))
                members_by_team_id.setdefault(member.team_id, []).append((member, user))

                # First team lead encountered (lowest membership id) wins so the
                # result is deterministic when a team has more than one lead.
                if member.is_team_lead and member.team_id not in lead_user_by_team_id:
                    lead_user_by_team_id[member.team_id] = user

            return teams, total, users_map, lead_user_by_team_id, members_by_team_id
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to list teams", internal_details=str(e)
            ) from e
