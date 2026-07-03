from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.organization.domain.entities.organization_media_entity import (
    OrganizationMediaEntity,
)


class IOrganizationMediaRepository(ABC):
    """
    Repository interface for organization media.
    """

    session: AsyncSession

    @abstractmethod
    async def add(
        self,
        entity: OrganizationMediaEntity,
        *,
        audit: bool = True,
    ) -> OrganizationMediaEntity:
        """
        Adds organization media.
        """

    @abstractmethod
    async def get_by(self, **criteria) -> OrganizationMediaEntity | None:
        """
        Retrieves organization media by given criteria.
        """

    @abstractmethod
    async def update(
        self,
        entity: OrganizationMediaEntity,
        *,
        audit: bool = True,
    ) -> OrganizationMediaEntity:
        """
        Updates organization media.
        """
