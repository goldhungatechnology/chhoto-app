from src.modules.organization.domain.ports.organization_member.organization_member_reader import (
    OrganizationMemberReader,
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
from src.modules.workforce.presentation.schemas.team.team_schemas import (
    RelocateTeamMembersRequestSchema,
)
from src.shared.exceptions.base_exceptions import DomainError, InvalidError, ServerError


class RelocateTeamMembersUseCase:
    """
    Use case for relocating team members to a different team.
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
        source_team_uuid: str,
        payload: RelocateTeamMembersRequestSchema,
    ) -> None:
        """
        Executes the use case to relocate team members to a different team.
        """
        try:
            source_team = await self.team_domain_service.get_team_by_uuid(
                source_team_uuid
            )

            if not source_team or not source_team.id:
                raise InvalidError(
                    error=f"Source team with UUID '{source_team_uuid}' does not exist"
                )

            for member in payload.members:
                target_team = await self.team_domain_service.get_team_by_uuid(
                    member.new_team_uuid
                )
                if not target_team or not target_team.id:
                    raise InvalidError(
                        error=f"Target team with UUID '{member.new_team_uuid}' does not exist"
                    )

                org_members = await self.organization_member_reader.get_members_by_ids(
                    member_ids=[member.member_id]
                )

                if len(org_members) == 0:
                    raise InvalidError(
                        error=f"Member with UUID '{member.member_id}' does not exist in the organization"
                    )

                org_member = org_members[0]

                if not org_member or not org_member.id:
                    raise InvalidError(
                        error=f"Member with UUID '{member.member_id}' does not exist in the organization"
                    )

                # Remove the member from the source team even if they are lead of the team
                await self.team_member_domain_service.remove_team_member(
                    team_id=source_team.id,
                    member_id=org_member.id,
                    organization_id=self.organization_id,
                    allow_lead_removal=True,
                )

                # Add the member to the target team
                new_team_member = TeamMemberEntity(
                    team_id=target_team.id,
                    member_id=org_member.id,
                    role=member.role,
                )
                await self.team_member_domain_service.add_team_member(
                    team_member_entity=new_team_member,
                    organization_id=self.organization_id,
                    already_exists_failure=False,  ## if already a team member, don't fail, just return the existing one
                )

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to relocate team members", internal_details=str(e)
            ) from e
