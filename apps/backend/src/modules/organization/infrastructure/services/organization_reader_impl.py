from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.organization.domain.entities.organization_entity import (
    OrganizationEntity,
)
from src.modules.organization.domain.ports.organization.organization_reader import (
    OrganizationReader,
)
from src.modules.organization.domain.services.organization_domain_service import (
    OrganizationDomainService,
)
from src.modules.organization.infrastructure.repositories.organization_repository_impl import (
    OrganizationRepositoryImpl,
)


class OrganizationReaderImpl(OrganizationReader):
    """
    Implementation of the organization reader port for reading organization data.
    """

    def __init__(self, organization_domain_service: OrganizationDomainService):
        self.organization_domain_service = organization_domain_service

    async def get_organization(self, organization_id: int) -> OrganizationEntity | None:
        """
        Retrieves the organization associated with the given organization ID.
        """
        return await self.organization_domain_service.get_organization_by_id(
            organization_id
        )

    async def get_organization_by_uuid(
        self, organization_uuid: str
    ) -> OrganizationEntity | None:
        """
        Retrieves the organization associated with the given organization UUID.
        """
        return await self.organization_domain_service.get_organization_by_uuid(
            organization_uuid
        )

    async def get_organizations_by_user_id(
        self, user_id: int
    ) -> list[OrganizationEntity] | None:
        """
        Retrieves the organization associated with the given user ID.
        """
        return await self.organization_domain_service.list_organizations_by_user_id(
            user_id
        )


def get_organization_reader(session: AsyncSession):
    """
    Factory function to create an instance of OrganizationReaderImpl with the necessary dependencies.
    """
    organization_repository = OrganizationRepositoryImpl(session=session)
    organization_domain_service = OrganizationDomainService(
        repository=organization_repository
    )
    return OrganizationReaderImpl(
        organization_domain_service=organization_domain_service
    )
