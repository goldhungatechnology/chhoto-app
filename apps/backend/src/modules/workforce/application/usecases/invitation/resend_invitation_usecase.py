from src.modules.workforce.domain.entities.invitation.invitation_entity import (
    InvitationEntity,
)
from src.modules.workforce.domain.services.invitation.invitation_domain_service import (
    InvitationDomainService,
)
from src.shared.exceptions.base_exceptions import CreateError, DomainError
from src.shared.mediator.mediator import mediator


class ResendInvitationUseCase:
    """
    Admin action: resend an invitation. Revokes the existing row and issues a
    fresh one with a new token and TTL. Returns the new invitation and the
    new raw token (for email delivery).
    """

    def __init__(self, invitation_domain_service: InvitationDomainService):
        self.invitation_domain_service = invitation_domain_service

    async def execute(
        self, *, invitation_uuid: str, actor_id: int
    ) -> tuple[InvitationEntity, str]:
        try:
            new_invitation, raw_token = await self.invitation_domain_service.resend(
                invitation_uuid, actor_id=actor_id
            )

            for event in new_invitation.pull_events():
                await mediator.publish(event)

            return new_invitation, raw_token
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to resend invitation", internal_details=str(e)
            ) from e
