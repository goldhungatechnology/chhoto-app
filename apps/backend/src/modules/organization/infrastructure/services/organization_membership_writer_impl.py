from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.organization.domain.entities.organization_member_entity import (
    OrganizationMemberEntity,
)
from src.modules.organization.domain.ports.organization_member.organization_membership_writer import (
    OrganizationMembershipWriter,
)
from src.modules.organization.domain.services.organization_member_domain_service import (
    OrganizationMemberDomainService,
)
from src.modules.organization.infrastructure.repositories.organization_member_repository_impl import (
    OrganizationMemberRepositoryImpl,
)


class OrganizationMembershipWriterImpl(OrganizationMembershipWriter):
    """
    Implementation of the organization membership writer port.
    """

    def __init__(
        self,
        organization_member_domain_service: OrganizationMemberDomainService,
    ):
        self.organization_member_domain_service = organization_member_domain_service

    async def create_membership(
        self,
        *,
        organization_id: int,
        user_id: int,
        actor_id: int | None = None,
    ) -> OrganizationMemberEntity:
        membership = OrganizationMemberEntity(
            organization_id=organization_id,
            user_id=user_id,
            status="active",
            created_by_id=actor_id,
        )
        return await self.organization_member_domain_service.add_member(membership)


def get_organization_membership_writer(session: AsyncSession):
    """
    Factory bound to the caller's session so the write participates in the
    surrounding transaction.
    """
    repository = OrganizationMemberRepositoryImpl(session=session)
    domain_service = OrganizationMemberDomainService(repository=repository)
    return OrganizationMembershipWriterImpl(
        organization_member_domain_service=domain_service
    )
