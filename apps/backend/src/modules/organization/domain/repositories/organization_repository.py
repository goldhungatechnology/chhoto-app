from src.modules.organization.domain.entities.organization_entity import (
    OrganizationEntity,
)
from src.shared.domain.repository.base_repository_interface import IBaseRepository
from abc import abstractmethod


class IOrganizationRepository(IBaseRepository[OrganizationEntity]):
    """
    Interface for the organization repository.
    """

    @abstractmethod
    async def list_by_user_id(self, user_id: int) -> list[OrganizationEntity] | None:
        """
        Lists organizations associated with a given user ID.
        """
        pass
