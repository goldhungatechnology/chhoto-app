from fastapi.requests import Request
from typing import Any

from src.modules.organization.domain.services.organization_domain_service import (
    OrganizationDomainService,
)
from src.modules.organization.domain.services.organization_member_domain_service import (
    OrganizationMemberDomainService,
)
from src.modules.organization.infrastructure.repositories.organization_member_repository_impl import (
    OrganizationMemberRepositoryImpl,
)
from src.modules.organization.infrastructure.repositories.organization_repository_impl import (
    OrganizationRepositoryImpl,
)
from src.shared.exceptions.base_exceptions import (
    ForbiddenError,
    NotFoundError,
    ServerError,
)


class OrganizationDependency:
    """
    Class representing an organization dependency.
    It acts like an organization middleware, but instead of being a middleware, it is a dependency that can be injected into any endpoint or service that needs access to the organization context.
    """

    def __init__(self, check_user_org_access: bool = True):
        self.check_user_org_access = check_user_org_access

    async def __call__(self, request: Request) -> Any:
        """
        1. Extracts the organization ID from the request headers.
        2. Retrieves the organization details using the OrganizationDomainService.
        3. If the organization is not found, raises a NotFoundError.
        4. Returns the organization details.
        """
        from src.shared.infrastructure.db import async_session

        session = async_session()
        try:
            organization_id = request.headers.get("X-Organization-Id")
            if not organization_id:
                raise ForbiddenError(
                    error="Organization UUID is required in the X-Organization-Id header",
                    errors={"code": "ORGANIZATION_ID_MISSING"},
                )

            organization_domain_service = OrganizationDomainService(
                repository=OrganizationRepositoryImpl(session=session)
            )

            organization = await organization_domain_service.get_organization_by_uuid(
                uuid=organization_id
            )
            if not organization:
                raise NotFoundError(
                    error="Organization not found",
                    errors={"code": "ORGANIZATION_NOT_FOUND"},
                )
            if not organization.id:
                raise ServerError(
                    error="Server error: Organization ID is missing in the retrieved organization details",
                    internal_details=f"Organization details: id not found in organization entity with uuid {organization_id}",
                )

            if self.check_user_org_access:
                user_id = getattr(request.state, "user_id", None)
                if not user_id:
                    raise ForbiddenError(
                        error="User authentication required to access organization context",
                        errors={"code": "USER_AUTHENTICATION_REQUIRED"},
                    )
                organization_member_domain_service = OrganizationMemberDomainService(
                    repository=OrganizationMemberRepositoryImpl(session=session)
                )
                if not await organization_member_domain_service.is_organization_member(
                    user_id=user_id, organization_id=organization.id
                ):
                    raise ForbiddenError(
                        error="User does not have access to this organization",
                        errors={"code": "USER_NO_ORG_ACCESS"},
                    )

            request.state.organization_id = organization.id
            # Expose the authorized org's uuid so path-scoped endpoints can
            # confirm the resource in the URL matches the org the caller was
            # actually authorized for (prevents cross-org IDOR via the path).
            request.state.organization_uuid = organization.uuid
            return organization
        finally:
            await session.close()


def get_organization_dependency(
    check_user_org_access: bool = True,
) -> OrganizationDependency:
    """
    Factory function to create an instance of OrganizationDependency.
    """
    return OrganizationDependency(check_user_org_access=check_user_org_access)
