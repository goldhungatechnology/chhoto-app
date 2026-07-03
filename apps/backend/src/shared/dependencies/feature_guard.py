from enum import StrEnum
from functools import wraps
from typing import Any, Awaitable, Callable

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.billing.billing_container import get_billing_container
from src.shared.exceptions.base_exceptions import ForbiddenError
from src.shared.infrastructure.db import get_async_session


def require_feature(feature_key: str | StrEnum, amount: int = 1):
    """
    Dependency to check whether current organization can use a billing feature.
    """

    async def dependency(
        request: Request,
        session: AsyncSession = Depends(get_async_session),
    ):
        organization_id = getattr(request.state, "organization_id", None)

        if not organization_id:
            raise ForbiddenError(error="Organization context not found")

        normalized_feature_key = str(feature_key).strip().lower()

        billing_container = get_billing_container(
            session=session,
            organization_id=organization_id,
        )

        entitlement_service = billing_container.entitlement_domain_service()

        result = await entitlement_service.can_use_feature(
            organization_id=organization_id,
            feature_key=normalized_feature_key,
            amount=amount,
        )

        if not result["allowed"]:
            raise ForbiddenError(error=str(result["reason"]))

        return result

    return dependency


def require_feature_decorator(feature_key: str | StrEnum, amount: int = 1):
    """
    Decorator to check whether current otganization can usea billing feature.
    """

    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            request: Request | None = kwargs.get("request")
            session: AsyncSession | None = kwargs.get("session")

            if request is None:
                raise ForbiddenError(error="Request context not found")

            if session is None:
                raise ForbiddenError(error="Database session not found")

            organization_id = getattr(request.state, "organization_id", None)

            if not organization_id:
                raise ForbiddenError(error="Organization context not found")

            normalized_feature_key = str(feature_key).strip().lower()

            billing_container = get_billing_container(
                session=session,
                organization_id=organization_id,
            )

            entitlement_service = billing_container.entitlement_domain_service()

            result = await entitlement_service.can_use_feature(
                organization_id=organization_id,
                feature_key=normalized_feature_key,
                amount=amount,
            )

            if not result["allowed"]:
                raise ForbiddenError(error=str(result["reason"]))

            return await func(*args, **kwargs)

        return wrapper

    return decorator
