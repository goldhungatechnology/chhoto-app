from collections.abc import Iterable

from fastapi import Request

from src.modules.organization.domain.services.organization_member_domain_service import (
    OrganizationMemberDomainService,
)
from src.modules.organization.infrastructure.repositories.organization_member_repository_impl import (
    OrganizationMemberRepositoryImpl,
)
from src.modules.organization.infrastructure.services.member_role_reader_impl import (
    MemberRoleReaderImpl,
)
from src.shared.exceptions.base_exceptions import ForbiddenError


def require_org_role(allowed_roles: Iterable[str]):
    """
    Build a dependency that authorizes the caller only if they hold one of the
    given roles in the organization they are acting on.

    This MUST run after an access dependency that has already established
    `request.state.user_id` and `request.state.organization_id` (i.e. it is
    layered on top of `require_access(organization_member=True)`). It exists
    because organization membership alone is not sufficient for privileged
    actions — those require a management role (e.g. owner/admin).
    """
    allowed = {role.lower() for role in allowed_roles}

    async def dependency(request: Request) -> None:
        from src.shared.infrastructure.db import async_session

        user_id = getattr(request.state, "user_id", None)
        organization_id = getattr(request.state, "organization_id", None)
        if not user_id or not organization_id:
            raise ForbiddenError(
                error="Organization context is required for this action",
                errors={"code": "ORG_CONTEXT_REQUIRED"},
            )

        async with async_session() as session:
            member_domain_service = OrganizationMemberDomainService(
                repository=OrganizationMemberRepositoryImpl(session=session)
            )
            member = await member_domain_service.get_member_by_user_id(
                organization_id=organization_id, user_id=user_id
            )
            if not member or not member.id:
                raise ForbiddenError(
                    error="You do not have access to this organization",
                    errors={"code": "USER_NO_ORG_ACCESS"},
                )

            role_reader = MemberRoleReaderImpl(session=session)
            roles = await role_reader.get_member_roles([member.id])

        role = (roles.get(member.id) or "").lower()
        if role not in allowed:
            raise ForbiddenError(
                error="You do not have permission to perform this action",
                errors={"code": "INSUFFICIENT_ROLE"},
            )

    return dependency
