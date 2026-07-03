from typing import Any, Protocol

from src.shared.exceptions.base_exceptions import DomainError


class SubscriptionReader(Protocol):
    """Structural contract for reading the org's current subscription."""

    async def get_active_billing_subscription(self) -> Any: ...


class PlanLimitReader(Protocol):
    """Structural contract for reading a plan's feature limit."""

    async def get_plan_limit(self, plan_id: int, feature_key: str) -> Any: ...


class FeatureUsageReader(Protocol):
    """Structural contract for reading current feature usage."""

    async def get_usage(self, subscription_id: int, feature_key: str) -> Any: ...


class EntitlementDomainService:
    """
    Centralized service for billing entitlement logic.

    Collaborators are typed by structural Protocols rather than concrete
    classes so the service depends on behaviour, not implementations (and stays
    trivially testable with lightweight fakes).
    """

    def __init__(
        self,
        subscription_service: SubscriptionReader,
        plan_limit_service: PlanLimitReader,
        feature_usage_service: FeatureUsageReader,
    ):
        self.subscription_service = subscription_service
        self.plan_limit_service = plan_limit_service
        self.feature_usage_service = feature_usage_service

    async def can_use_feature(
        self,
        organization_id: int,
        feature_key: str,
        amount: int = 1,
    ) -> dict[str, bool | str | int | None]:
        """
        Check whether organization can use a feature.
        """
        try:
            feature_key = feature_key.strip().lower()

            active_subscription = (
                await self.subscription_service.get_active_billing_subscription()
            )

            if active_subscription is None or active_subscription.id is None:
                return {
                    "allowed": False,
                    "reason": "No active subscription found",
                    "remaining": 0,
                }

            allowed_statuses = {"active", "trialing"}
            if (
                active_subscription.status or ""
            ).strip().lower() not in allowed_statuses:
                return {
                    "allowed": False,
                    "reason": f"Subscription status is {active_subscription.status}",
                    "remaining": 0,
                }

            plan_limit = await self.plan_limit_service.get_plan_limit(
                plan_id=active_subscription.plan_id,
                feature_key=feature_key,
            )

            if plan_limit is None:
                return {
                    "allowed": False,
                    "reason": "Feature limit not configured",
                    "remaining": 0,
                }

            if plan_limit.is_unlimited:
                return {
                    "allowed": True,
                    "reason": None,
                    "remaining": -1,
                }

            feature_usage = await self.feature_usage_service.get_usage(
                subscription_id=active_subscription.id,
                feature_key=feature_key,
            )

            current_usage = feature_usage.used_value if feature_usage else 0
            limit_value = int(plan_limit.limit_value or 0)

            if current_usage + amount > limit_value:
                return {
                    "allowed": False,
                    "reason": "Feature usage limit exceeded",
                    "remaining": max(limit_value - current_usage, 0),
                }

            return {
                "allowed": True,
                "reason": None,
                "remaining": limit_value - (current_usage + amount),
            }

        except Exception as e:
            raise DomainError(
                error="Failed to validate feature entitlement",
                internal_details=str(e),
            ) from e
