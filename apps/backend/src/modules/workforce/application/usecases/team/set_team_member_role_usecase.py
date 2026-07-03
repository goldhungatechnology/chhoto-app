from src.modules.organization.domain.ports.organization_member.organization_member_reader import (
    OrganizationMemberReader,
)
from src.modules.workforce.application.usecases.team.team_member_guards import (
    ensure_member_belongs_to_org,
)
from src.modules.workforce.domain.entities.team.team_member_entity import (
    TeamMemberEntity,
)
from src.modules.workforce.domain.services.team.team_domain_service import (
    TeamDomainService,
)
from src.modules.workforce.domain.services.team.team_member_domain_service import (
    TeamMemberDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, UpdateError
from src.shared.mediator.mediator import mediator


class SetTeamMemberRoleUseCase:
    """
    Use case for changing a team member's role (member, supervisor, team lead).
    """

    def __init__(
        self,
        team_domain_service: TeamDomainService,
        team_member_domain_service: TeamMemberDomainService,
        organization_member_reader: OrganizationMemberReader,
        organization_id: int,
    ):
        self.team_domain_service = team_domain_service
        self.team_member_domain_service = team_member_domain_service
        self.organization_member_reader = organization_member_reader
        self.organization_id = organization_id

    async def execute(
        self,
        *,
        team_uuid: str,
        member_id: int,
        role: str,
        actor_id: int,
    ) -> TeamMemberEntity:
        """
        Executes the use case to change a team member's role.
        """
        try:
            await ensure_member_belongs_to_org(
                self.organization_member_reader, member_id, self.organization_id
            )

            team = await self.team_domain_service.get_team_by_uuid(team_uuid)
            if not team.id:
                raise UpdateError(error="Team not found")

            updated = await self.team_member_domain_service.set_member_role(
                team_id=team.id,
                member_id=member_id,
                role=role,
                organization_id=self.organization_id,
                actor_id=actor_id,
            )

            for event in updated.pull_events():
                await mediator.publish(event)

            return updated
        except DomainError:
            raise
        except Exception as e:
            raise UpdateError(
                error="Failed to set team member role", internal_details=str(e)
            ) from e
