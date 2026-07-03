from src.modules.organization.domain.ports.member_role.member_role_reader import (
    MemberRoleReader,
)
from src.modules.organization.domain.ports.organization_member.organization_member_reader import (
    OrganizationMemberReader,
)
from src.modules.workforce.application.usecases.team.team_member_guards import (
    ensure_member_belongs_to_org,
)
from src.modules.workforce.domain.services.team.team_domain_service import (
    TeamDomainService,
)
from src.modules.workforce.domain.services.team.team_member_domain_service import (
    TeamMemberDomainService,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    DeleteError,
    DomainError,
)
from src.shared.mediator.mediator import mediator

# The organization owner's role name, as seeded in default_roles. The owner is
# the permanent anchor of the default team and cannot be removed from it.
_OWNER_ROLE = "owner"


class RemoveTeamMemberUseCase:
    """
    Use case for removing a member from a team.
    """

    def __init__(
        self,
        team_domain_service: TeamDomainService,
        team_member_domain_service: TeamMemberDomainService,
        organization_member_reader: OrganizationMemberReader,
        member_role_reader: MemberRoleReader,
        organization_id: int,
    ):
        self.team_domain_service = team_domain_service
        self.team_member_domain_service = team_member_domain_service
        self.organization_member_reader = organization_member_reader
        self.member_role_reader = member_role_reader
        self.organization_id = organization_id

    async def execute(self, *, team_uuid: str, member_id: int) -> None:
        """
        Executes the use case to remove a member from a team.
        """
        try:
            await ensure_member_belongs_to_org(
                self.organization_member_reader, member_id, self.organization_id
            )

            team = await self.team_domain_service.get_team_by_uuid(team_uuid)
            if not team.id:
                raise DeleteError(error="Team not found")

            # The default team is seeded with the organization owner and can
            # never be deleted; for the same reason the owner cannot be removed
            # from it. Removal of the team lead is blocked in the domain service.
            if team.is_default:
                await self._ensure_not_organization_owner(member_id)

            removed_member = await self.team_member_domain_service.remove_team_member(
                team_id=team.id,
                member_id=member_id,
                organization_id=self.organization_id,
            )

            for event in removed_member.pull_events():
                await mediator.publish(event)
        except DomainError:
            raise
        except Exception as e:
            raise DeleteError(
                error="Failed to remove team member", internal_details=str(e)
            ) from e

    async def _ensure_not_organization_owner(self, member_id: int) -> None:
        """
        Reject removing the organization owner from the default team. Other
        members may be removed from the default team freely.
        """
        roles = await self.member_role_reader.get_member_roles([member_id])
        if (roles.get(member_id) or "").lower() == _OWNER_ROLE:
            raise ConflictError(
                error="The organization owner cannot be removed from the default team"
            )
