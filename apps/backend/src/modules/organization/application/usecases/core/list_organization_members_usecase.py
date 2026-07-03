from src.modules.auth.domain.ports.user.user_reader import UserReader
from src.modules.organization.domain.entities.organization_member_entity import (
    OrganizationMemberEntity,
)
from src.modules.organization.domain.ports.member_role.member_role_reader import (
    MemberRoleReader,
)
from src.modules.organization.domain.services.organization_member_domain_service import (
    OrganizationMemberDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class ListOrganizationMembersUseCase:
    """
    Page through organization members and enrich each row with the underlying
    user's profile and assigned role. Returns (members, total, users_by_id,
    roles_by_member_id) so the router can render rich responses without doing
    its own joins.
    """

    def __init__(
        self,
        organization_member_domain_service: OrganizationMemberDomainService,
        user_reader: UserReader,
        member_role_reader: MemberRoleReader,
    ):
        self.organization_member_domain_service = organization_member_domain_service
        self.user_reader = user_reader
        self.member_role_reader = member_role_reader

    async def execute(
        self,
        *,
        organization_id: int,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[OrganizationMemberEntity], int, dict, dict[int, str | None]]:
        try:
            (
                members,
                total,
            ) = await self.organization_member_domain_service.list_paginated(
                organization_id=organization_id,
                status=status,
                limit=limit,
                offset=offset,
            )

            user_ids = list({m.user_id for m in members})
            users = await self.user_reader.get_users_by_ids(user_ids)
            users_by_id = {u.id: u for u in users}

            member_ids = [m.id for m in members if m.id is not None]
            roles_by_member_id = await self.member_role_reader.get_member_roles(
                member_ids
            )

            return members, total, users_by_id, roles_by_member_id
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to list organization members",
                internal_details=str(e),
            ) from e
