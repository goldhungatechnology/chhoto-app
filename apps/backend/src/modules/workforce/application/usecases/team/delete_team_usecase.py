from src.modules.workforce.domain.services.team.team_domain_service import (
    TeamDomainService,
)
from src.modules.workforce.domain.services.team.team_member_domain_service import (
    TeamMemberDomainService,
)
from src.shared.exceptions.base_exceptions import DeleteError, DomainError, InvalidError
from src.shared.mediator.mediator import mediator


class DeleteTeamUseCase:
    """
    Use case for deleting (soft-delete) an existing team.
    """

    def __init__(
        self,
        team_domain_service: TeamDomainService,
        team_member_domain_service: TeamMemberDomainService,
    ):
        self.team_domain_service = team_domain_service
        self.team_member_domain_service = team_member_domain_service

    async def execute(self, team_uuid: str) -> None:
        """
        Executes the use case to delete a team and clear its memberships.
        """
        try:
            team_exists = await self.team_domain_service.get_team_by_uuid(team_uuid)
            if not team_exists or not team_exists.id:
                raise InvalidError(error=f"Team with UUID '{team_uuid}' does not exist")

            ## checking if member is assigned to a team or not
            if await self._check_team_members_relocation_required(team_exists.id):
                raise InvalidError(
                    error="Cannot delete team with assigned members. Please relocate members before deletion.",
                    errors={"code": "TEAM_MEMBERS_RELOCATION_REQUIRED"},
                )

            deleted_team = await self.team_domain_service.delete_team(team_uuid)
            if deleted_team and deleted_team.id:
                await self.team_member_domain_service.remove_all_members(
                    deleted_team.id
                )

            for event in deleted_team.pull_events():
                await mediator.publish(event)
        except DomainError:
            raise
        except Exception as e:
            raise DeleteError(
                error="Failed to delete team", internal_details=str(e)
            ) from e

    async def _check_team_members_relocation_required(self, team_id: int) -> bool:
        """
        Checks if any members of the team need to be relocated before deletion.
        Returns True if relocation is required, False otherwise.
        """
        try:
            members = await self.team_member_domain_service.list_team_members(team_id)
            return len(members) > 0
        except Exception as e:
            raise DeleteError(
                error="Failed to check team members for relocation",
                internal_details=str(e),
            ) from e
