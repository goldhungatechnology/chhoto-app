from abc import ABC, abstractmethod

from src.modules.organization.domain.entities.organization_entity import (
    OrganizationEntity,
)


class OrganizationReader(ABC):
    """
    organization reader port for reading organization data.
    """

    @abstractmethod
    async def get_organization(self, organization_id: int) -> OrganizationEntity | None:
        """
        Retrieves the organization associated with the given organization ID.
        """

    @abstractmethod
    async def get_organization_by_uuid(
        self, organization_uuid: str
    ) -> OrganizationEntity | None:
        """
        Retrieves the organization associated with the given organization UUID.
        """

    @abstractmethod
    async def get_organizations_by_user_id(
        self, user_id: int
    ) -> list[OrganizationEntity] | None:
        """
        Retrieves the organizations associated with the given user ID.
        """
