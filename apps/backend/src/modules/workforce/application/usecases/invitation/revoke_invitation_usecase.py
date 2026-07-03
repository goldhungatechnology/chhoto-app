from src.modules.workforce.domain.services.invitation.invitation_domain_service import (
    InvitationDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, UpdateError
from src.shared.mediator.mediator import mediator


class RevokeInvitationUseCase:
    """
    Admin action: revoke a pending invitation. Idempotent — revoking an
    already-revoked invitation succeeds silently. Accepted invitations cannot
    be revoked (the domain service rejects).
    """

    def __init__(self, invitation_domain_service: InvitationDomainService):
        self.invitation_domain_service = invitation_domain_service

    async def execute(self, invitation_uuid: str):
        try:
            revoked = await self.invitation_domain_service.revoke(invitation_uuid)

            for event in revoked.pull_events():
                await mediator.publish(event)
            return revoked
        except DomainError:
            raise
        except Exception as e:
            raise UpdateError(
                error="Failed to revoke invitation", internal_details=str(e)
            ) from e
