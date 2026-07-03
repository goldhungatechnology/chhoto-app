from src.modules.auth.domain.ports.user.user_reader import UserReader
from src.modules.workforce.domain.services.team.team_domain_service import (
    TeamDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class GetTeamUseCase:
    """
    Use case for retrieving a single team by its UUID.
    """

    def __init__(
        self,
        team_domain_service: TeamDomainService,
        user_reader: UserReader,
    ):
        self.team_domain_service = team_domain_service
        self.user_reader = user_reader

    async def execute(self, team_uuid: str):
        """
        Executes the use case to retrieve a team along with the actor who created it.
        """
        try:
            team = await self.team_domain_service.get_team_by_uuid(team_uuid)

            created_by = None
            if team.created_by_id is not None:
                created_by = await self.user_reader.get_user(team.created_by_id)

            return team, created_by
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to retrieve team", internal_details=str(e)
            ) from e
