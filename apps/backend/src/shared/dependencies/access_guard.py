from dataclasses import dataclass

from fastapi import Request

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.organization.domain.entities.organization_entity import (
    OrganizationEntity,
)
from src.shared.dependencies.org_dependency import get_organization_dependency
from src.shared.exceptions.base_exceptions import UnAuthorizedError
from src.shared.infrastructure.guards.user_guards import (
    require_onboarding,
    require_verified_email,
)


@dataclass(frozen=True)
class AccessContext:
    """
    AccessContext is a dataclass that encapsulates the user and organization information for a request. It is used to provide a consistent structure for access-related data throughout the application, making it easier to manage and enforce access control policies based on the user's authentication status, email verification, onboarding completion, and organization membership.
    """

    user: UserEntity | None = None
    organization: OrganizationEntity | None = None


def require_access(
    *,
    authenticated: bool = True,
    email_verified: bool = False,
    onboarded: bool = False,
    organization_member: bool = False,
):
    """
    Build a reusable access dependency for router/endpoint-level authorization.
    """
    needs_user = authenticated or email_verified or onboarded
    organization_dependency = (
        get_organization_dependency(check_user_org_access=True)
        if organization_member
        else None
    )

    async def dependency(
        request: Request,
    ) -> AccessContext:
        user_obj = getattr(request.state, "user", None)
        user = user_obj if isinstance(user_obj, UserEntity) else None
        organization: OrganizationEntity | None = None

        if needs_user:
            if user is None:
                raise UnAuthorizedError(
                    error="Authentication required",
                    errors={"code": "UNAUTHENTICATED"},
                )

        if email_verified and user is not None:
            require_verified_email(user)

        if onboarded and user is not None:
            require_onboarding(user)

        if organization_dependency is not None:
            organization = await organization_dependency(request)

        return AccessContext(user=user, organization=organization)

    return dependency
