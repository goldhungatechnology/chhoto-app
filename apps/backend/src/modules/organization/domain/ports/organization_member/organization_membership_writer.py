from abc import ABC, abstractmethod

from src.modules.organization.domain.entities.organization_member_entity import (
    OrganizationMemberEntity,
)


class OrganizationMembershipWriter(ABC):
    """
    Write-side port for organization membership operations. Exposed to other
    bounded contexts (e.g. workforce/invitations) that need to materialize an
    organization member without reaching into organization-internal services.
    """

    @abstractmethod
    async def create_membership(
        self,
        *,
        organization_id: int,
        user_id: int,
        actor_id: int | None = None,
    ) -> OrganizationMemberEntity:
        """
        Create an active organization membership for the given user.
        Raises ConflictError if the user is already an active member.
        """
