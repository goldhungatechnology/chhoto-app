from dataclasses import dataclass

from fastapi import Request

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.shared.exceptions.base_exceptions import UnAuthorizedError
from src.shared.infrastructure.guards.user_guards import (
    require_onboarding,
    require_verified_email,
)


@dataclass(frozen=True)
class AccessContext:
    """
    AccessContext is a dataclass that encapsulates the user information for a request.
    """

    user: UserEntity | None = None


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

    async def dependency(
        request: Request,
    ) -> AccessContext:
        user_obj = getattr(request.state, "user", None)
        user = user_obj if isinstance(user_obj, UserEntity) else None

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

        return AccessContext(user=user)

    return dependency
