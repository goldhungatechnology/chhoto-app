from abc import abstractmethod

from src.modules.workforce.domain.entities.invitation.invitation_entity import (
    InvitationEntity,
)
from src.shared.domain.repository.organization_repository_interface import (
    IOrganizationRepository,
)


class IInvitationRepository(IOrganizationRepository[InvitationEntity]):
    """
    Repository interface for managing InvitationEntity instances.
    """

    @abstractmethod
    async def get_by_hashed_token(self, hashed_token: str) -> InvitationEntity | None:
        """
        Lookup an invitation by its deterministic-hashed token.
        NOTE: This lookup is NOT organization-scoped because the public
        accept/view endpoints don't know the organization yet — the token
        itself is what proves authority.
        """

    @abstractmethod
    async def mark_accepted_if_pending(
        self, invitation_id: int
    ) -> InvitationEntity | None:
        """
        Atomically flip a 'pending' invitation to 'accepted', returning the
        updated entity or None if it was not pending (compare-and-set guard
        against concurrent double-accept).
        """
