from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.organization.domain.entities.organization_member_entity import (
    OrganizationMemberEntity,
)
from src.modules.organization.domain.ports.organization_member.organization_member_reader import (
    OrganizationMemberReader,
)
from src.modules.organization.domain.services.organization_member_domain_service import (
    OrganizationMemberDomainService,
)
from src.modules.organization.infrastructure.repositories.organization_member_repository_impl import (
    OrganizationMemberRepositoryImpl,
)


class OrganizationMemberReaderImpl(OrganizationMemberReader):
    """
    Implementation of the organization member reader port.
    """

    def __init__(
        self,
        organization_member_domain_service: OrganizationMemberDomainService,
    ):
        self.organization_member_domain_service = organization_member_domain_service

    async def get_members_by_ids(
        self, member_ids: list[int]
    ) -> list[OrganizationMemberEntity]:
        return await self.organization_member_domain_service.get_members_by_ids(
            member_ids
        )

    async def get_member_by_user_id(
        self, organization_id: int, user_id: int
    ) -> OrganizationMemberEntity | None:
        return await self.organization_member_domain_service.get_member_by_user_id(
            organization_id, user_id
        )

    async def get_members_by_user_ids(
        self, organization_id: int, user_ids: list[int]
    ) -> list[OrganizationMemberEntity]:
        return await self.organization_member_domain_service.get_members_by_user_ids(
            organization_id, user_ids
        )

    async def get_member_by_uuids(
        self, organization_id: int, member_uuid: str
    ) -> OrganizationMemberEntity | None:
        return await self.organization_member_domain_service.get_member_by_uuids(
            organization_id, member_uuid
        )


def get_organization_member_reader(session: AsyncSession):
    """
    Factory function to create an instance of OrganizationMemberReaderImpl with
    the necessary dependencies bound to the caller's session.
    """
    repository = OrganizationMemberRepositoryImpl(session=session)
    domain_service = OrganizationMemberDomainService(repository=repository)
    return OrganizationMemberReaderImpl(
        organization_member_domain_service=domain_service
    )
