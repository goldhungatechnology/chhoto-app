from src.modules.workforce.domain.entities.invitation.invitation_entity import (
    InvitationEntity,
)
from src.modules.workforce.domain.services.invitation.invitation_domain_service import (
    InvitationDomainService,
)
from src.modules.workforce.domain.services.rbac.rbac_role_domain_service import (
    RbacRoleDomainService,
)
from src.modules.workforce.domain.services.team.team_domain_service import (
    TeamDomainService,
)
from src.shared.exceptions.base_exceptions import (
    CreateError,
    DomainError,
    NotFoundError,
)
from src.shared.mediator.mediator import mediator


class CreateInvitationUseCase:
    """
    Admin action: invite a new user (by email) to the organization, assigning
    them a role and optionally placing them on a team.

    The API accepts public UUIDs (role_uuid, team_uuid) and this use case
    resolves them to internal numeric IDs before handing off to the domain
    service. The domain layer stays unaware of UUID-vs-ID concerns.
    """

    def __init__(
        self,
        invitation_domain_service: InvitationDomainService,
        rbac_role_domain_service: RbacRoleDomainService,
        team_domain_service: TeamDomainService,
    ):
        self.invitation_domain_service = invitation_domain_service
        self.rbac_role_domain_service = rbac_role_domain_service
        self.team_domain_service = team_domain_service

    async def execute(
        self,
        *,
        organization_id: int,
        email: str,
        role_uuid: str,
        team_uuid: str | None,
        actor_id: int,
    ) -> tuple[InvitationEntity, str]:
        try:
            normalized_email = email.strip().lower()

            role = await self.rbac_role_domain_service.get_role_by_uuid(role_uuid)
            if not role or not role.id:
                raise NotFoundError(error="Role not found")

            team_id: int | None = None
            if team_uuid is not None:
                team = await self.team_domain_service.get_team_by_uuid(team_uuid)
                if not team.id:
                    raise NotFoundError(error="Team not found")
                team_id = team.id

            (
                invitation,
                raw_token,
            ) = await self.invitation_domain_service.create_invitation(
                organization_id=organization_id,
                email=normalized_email,
                role_id=role.id,
                team_id=team_id,
                invited_by_id=actor_id,
            )

            for event in invitation.pull_events():
                await mediator.publish(event)

            return invitation, raw_token
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to create invitation", internal_details=str(e)
            ) from e
