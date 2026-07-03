from abc import abstractmethod

from src.modules.organization.domain.entities.organization_member_entity import (
    OrganizationMemberEntity,
)
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IOrganizationMemberRepository(IBaseRepository[OrganizationMemberEntity]):
    """
    Interface for the organization member repository.
    """

    @abstractmethod
    async def list_paginated(
        self,
        *,
        organization_id: int,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[OrganizationMemberEntity], int]:
        """
        List organization members for the given org, optionally filtered by
        status. Returns the slice plus the total count for pagination metadata.
        """
