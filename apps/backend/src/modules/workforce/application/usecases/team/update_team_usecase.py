from src.modules.workforce.domain.entities.team.team_entity import TeamEntity
from src.modules.workforce.domain.services.team.team_domain_service import (
    TeamDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, UpdateError
from src.shared.mediator.mediator import mediator


class UpdateTeamUseCase:
    """
    Use case for updating an existing team.
    """

    def __init__(self, team_domain_service: TeamDomainService):
        self.team_domain_service = team_domain_service

    async def execute(
        self,
        *,
        team_uuid: str,
        actor_id: int,
        name: str | None = None,
        description: str | None = None,
        color: str | None = None,
        timezone: str | None = None,
        is_default: bool | None = None,
    ) -> TeamEntity:
        """
        Executes the use case to update an existing team.
        """
        try:
            updated_team = await self.team_domain_service.update_team(
                team_uuid=team_uuid,
                name=name,
                description=description,
                color=color,
                timezone=timezone,
                is_default=is_default,
                actor_id=actor_id,
            )

            for event in updated_team.pull_events():
                await mediator.publish(event)

            return updated_team
        except DomainError:
            raise
        except Exception as e:
            raise UpdateError(
                error="Failed to update team", internal_details=str(e)
            ) from e
