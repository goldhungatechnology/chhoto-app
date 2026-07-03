from src.modules.organization.domain.ports.organization_member.organization_member_reader import (
    OrganizationMemberReader,
)
from src.modules.workforce.domain.entities.team.team_entity import TeamEntity
from src.modules.workforce.domain.entities.team.team_member_entity import (
    TeamMemberEntity,
    TeamMemberRole,
)
from src.modules.workforce.domain.services.team.team_domain_service import (
    TeamDomainService,
)
from src.modules.workforce.domain.services.team.team_member_domain_service import (
    TeamMemberDomainService,
)
from src.shared.exceptions.base_exceptions import CreateError, DomainError
from src.shared.mediator.mediator import mediator


class CreateTeamUseCase:
    """
    Use case for creating a new team. The creator is automatically added as a
    team member and promoted to team lead.
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
        organization_id: int,
        name: str,
        description: str | None,
        color: str | None,
        timezone: str | None,
        is_default: bool,
        actor_id: int,
    ) -> TeamEntity:
        """
        Executes the use case to create a new team and register the creator as
        its team lead.
        """
        try:
            team_entity = TeamEntity(
                organization_id=organization_id,
                name=name,
                description=description,
                color=TeamEntity.get_random_color(),
                timezone=timezone,
                is_default=is_default,
                created_by_id=actor_id,
            )

            new_team = await self.team_domain_service.create_team(team_entity)
            if not new_team or not new_team.id:
                raise CreateError(error="Failed to create team")

            for event in new_team.pull_events():
                await mediator.publish(event)

            # Register the creator as the team's first member and team lead.
            # `team_members.member_id` references the organization-membership
            # row, so resolve the actor's membership before adding.
            actor_member = await self.organization_member_reader.get_member_by_user_id(
                organization_id, actor_id
            )
            if not actor_member or not actor_member.id:
                raise CreateError(
                    error="Failed to create team",
                    internal_details=(
                        f"actor_id={actor_id} is not an active member of "
                        f"organization_id={organization_id}"
                    ),
                )

            team_member_entity = TeamMemberEntity(
                team_id=new_team.id,
                member_id=actor_member.id,
                role=TeamMemberRole.TEAM_LEAD,
                created_by_id=actor_id,
            )
            new_team_member = await self.team_member_domain_service.add_team_member(
                team_member_entity, organization_id=organization_id
            )

            for event in new_team_member.pull_events():
                await mediator.publish(event)

            return new_team
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to create team", internal_details=str(e)
            ) from e
