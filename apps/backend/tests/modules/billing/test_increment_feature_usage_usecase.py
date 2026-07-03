import pytest

from src.modules.billing.application.usecases.increment_feature_usage_usecase import (
    IncrementFeatureUsageUseCase,
)


class FakeSubscription:
    def __init__(self):
        self.id = 1


class FakeSubscriptionService:
    async def get_active_billing_subscription(self):
        return FakeSubscription()


class FakeFeatureUsageService:
    def __init__(self):
        self.increment_called = False
        self.subscription_id = None
        self.feature_key = None
        self.amount = None

    async def increment_usage(
        self,
        subscription_id: int,
        feature_key: str,
        amount: int,
    ):
        self.increment_called = True
        self.subscription_id = subscription_id
        self.feature_key = feature_key
        self.amount = amount


@pytest.mark.asyncio
async def test_increment_feature_usage_usecase_success():
    subscription_service = FakeSubscriptionService()
    feature_usage_service = FakeFeatureUsageService()

    use_case = IncrementFeatureUsageUseCase(
        subscription_service=subscription_service,
        feature_usage_service=feature_usage_service,
    )

    await use_case.execute(
        feature_key="agents",
        amount=1,
    )

    assert feature_usage_service.increment_called is True
    assert feature_usage_service.subscription_id == 1
    assert feature_usage_service.feature_key == "agents"
    assert feature_usage_service.amount == 1
