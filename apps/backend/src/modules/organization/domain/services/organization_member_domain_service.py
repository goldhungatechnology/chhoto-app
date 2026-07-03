from src.modules.organization.domain.entities.organization_member_entity import (
    OrganizationMemberEntity,
)
from src.modules.organization.domain.repositories.organization_member_repository import (
    IOrganizationMemberRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    CreateError,
    DomainError,
)


class OrganizationMemberDomainService:
    """
    Service class for organization member domain logic.
    """

    def __init__(self, repository: IOrganizationMemberRepository):
        self.repository = repository

    async def add_member(
        self, member_entity: OrganizationMemberEntity
    ) -> OrganizationMemberEntity:
        """
        Adds user as organization member.
        """
        try:
            existing_member = await self.repository.get_by(
                organization_id=member_entity.organization_id,
                user_id=member_entity.user_id,
                status="active",
            )
            if existing_member:
                raise ConflictError(
                    error="User is already a member of this organization"
                )

            return await self.repository.add(member_entity)
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to add organization member", internal_details=str(e)
            ) from e

    async def is_organization_member(self, organization_id: int, user_id: int) -> bool:
        """
        Checks if a user is an active member of the organization.
        """
        member = await self.repository.get_by(
            organization_id=organization_id, user_id=user_id, status="active"
        )
        return member is not None

    async def get_member_by_user_id(
        self, organization_id: int, user_id: int
    ) -> OrganizationMemberEntity | None:
        """
        Returns the active membership row for a user in an organization (or None).
        """
        return await self.repository.get_by(
            organization_id=organization_id, user_id=user_id, status="active"
        )

    async def get_members_by_ids(
        self, member_ids: list[int]
    ) -> list[OrganizationMemberEntity]:
        """
        Retrieves organization members by a list of internal IDs.
        Empty list short-circuits to avoid an empty IN-clause.
        """
        if not member_ids:
            return []
        return await self.repository.filter(id__in=member_ids)

    async def get_member_by_uuids(
        self, organization_id: int, member_uuid: str
    ) -> OrganizationMemberEntity | None:
        """
        Retrieves an active organization member by UUID.
        """
        return await self.repository.get_by(
            organization_id=organization_id, uuid=member_uuid, status="active"
        )

    async def get_members_by_user_ids(
        self, organization_id: int, user_ids: list[int]
    ) -> list[OrganizationMemberEntity]:
        """
        Retrieves active organization members for a list of user IDs within an
        organization. Empty input short-circuits to avoid an empty IN-clause.
        """
        if not user_ids:
            return []
        return await self.repository.filter(
            organization_id=organization_id, user_id__in=user_ids, status="active"
        )

    async def list_paginated(
        self,
        *,
        organization_id: int,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[OrganizationMemberEntity], int]:
        """
        Page through organization members, optionally filtered by status.
        """
        try:
            return await self.repository.list_paginated(
                organization_id=organization_id,
                status=status,
                limit=limit,
                offset=offset,
            )
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to list organization members",
                internal_details=str(e),
            ) from e
