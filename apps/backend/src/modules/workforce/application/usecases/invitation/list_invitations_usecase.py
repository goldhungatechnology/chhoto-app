from src.modules.auth.domain.ports.user.user_reader import UserReader
from src.modules.workforce.domain.entities.invitation.invitation_entity import (
    InvitationEntity,
)
from src.modules.workforce.domain.services.invitation.invitation_domain_service import (
    InvitationDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class ListInvitationsUseCase:
    """
    Lists invitations within the current organization. Resolves the `invited_by`
    user for each row so the API can render who issued the invite.
    """

    def __init__(
        self,
        invitation_domain_service: InvitationDomainService,
        user_reader: UserReader,
    ):
        self.invitation_domain_service = invitation_domain_service
        self.user_reader = user_reader

    async def execute(
        self, *, status: str | None = None
    ) -> tuple[list[InvitationEntity], dict]:
        try:
            invitations = await self.invitation_domain_service.list_for_organization(
                status=status
            )

            user_ids = {inv.invited_by_id for inv in invitations if inv.invited_by_id}
            users = await self.user_reader.get_users_by_ids(list(user_ids))
            users_by_id = {u.id: u for u in users}

            return invitations, users_by_id
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to list invitations", internal_details=str(e)
            ) from e
