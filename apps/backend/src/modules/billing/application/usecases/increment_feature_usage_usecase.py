from typing import Any, Protocol

from src.shared.exceptions.base_exceptions import ServerError


class SubscriptionReader(Protocol):
    """Structural contract for reading the org's current subscription."""

    async def get_active_billing_subscription(self) -> Any: ...


class FeatureUsageIncrementer(Protocol):
    """Structural contract for incrementing feature usage."""

    async def increment_usage(
        self, subscription_id: int, feature_key: str, amount: int
    ) -> Any: ...


class IncrementFeatureUsageUseCase:
    """
    Use case for incrementing feature usage after successful action.

    Collaborators are typed by structural Protocols rather than concrete
    classes so the use case depends on behaviour, not implementations.
    """

    def __init__(
        self,
        subscription_service: SubscriptionReader,
        feature_usage_service: FeatureUsageIncrementer,
    ):
        self.subscription_service = subscription_service
        self.feature_usage_service = feature_usage_service

    async def execute(
        self,
        feature_key: str,
        amount: int = 1,
    ) -> None:
        try:
            active_subscription = (
                await self.subscription_service.get_active_billing_subscription()
            )

            if not active_subscription or not active_subscription.id:
                raise ServerError(error="Active subscription not found")

            await self.feature_usage_service.increment_usage(
                subscription_id=active_subscription.id,
                feature_key=feature_key,
                amount=amount,
            )

        except Exception as e:
            raise ServerError(
                error="Failed to increment feature usage",
                internal_details=str(e),
            ) from e
