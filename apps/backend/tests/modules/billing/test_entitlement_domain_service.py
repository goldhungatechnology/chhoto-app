import pytest

from src.modules.billing.domain.services.entitlement_domain_service import (
    EntitlementDomainService,
)


class FakeSubscription:
    def __init__(
        self,
        *,
        subscription_id: int = 1,
        plan_id: int = 1,
        status: str = "active",
    ):
        self.id = subscription_id
        self.plan_id = plan_id
        self.status = status


class FakePlanLimit:
    def __init__(
        self,
        *,
        limit_value: int | None = 10,
        is_unlimited: bool = False,
    ):
        self.limit_value = limit_value
        self.is_unlimited = is_unlimited


class FakeFeatureUsage:
    def __init__(self, *, used_value: int = 5):
        self.used_value = used_value


class FakeSubscriptionService:
    def __init__(self, subscription=None):
        self.subscription = subscription

    async def get_active_billing_subscription(self):
        return self.subscription


class FakePlanLimitService:
    def __init__(self, plan_limit=None):
        self.plan_limit = plan_limit

    async def get_plan_limit(self, plan_id: int, feature_key: str):
        return self.plan_limit


class FakeFeatureUsageService:
    def __init__(self, usage=None):
        self.usage = usage

    async def get_usage(self, subscription_id: int, feature_key: str):
        return self.usage


@pytest.mark.asyncio
async def test_can_use_feature_allows_when_usage_is_under_limit():
    entitlement_service = EntitlementDomainService(
        subscription_service=FakeSubscriptionService(
            subscription=FakeSubscription(status="active")
        ),
        plan_limit_service=FakePlanLimitService(
            plan_limit=FakePlanLimit(limit_value=10, is_unlimited=False)
        ),
        feature_usage_service=FakeFeatureUsageService(
            usage=FakeFeatureUsage(used_value=5)
        ),
    )

    result = await entitlement_service.can_use_feature(
        organization_id=10,
        feature_key="max_users",
        amount=1,
    )

    assert result["allowed"] is True
    assert result["reason"] is None
    assert result["remaining"] == 4


@pytest.mark.asyncio
async def test_can_use_feature_denies_when_usage_exceeds_limit():
    entitlement_service = EntitlementDomainService(
        subscription_service=FakeSubscriptionService(
            subscription=FakeSubscription(status="active")
        ),
        plan_limit_service=FakePlanLimitService(
            plan_limit=FakePlanLimit(limit_value=10, is_unlimited=False)
        ),
        feature_usage_service=FakeFeatureUsageService(
            usage=FakeFeatureUsage(used_value=10)
        ),
    )

    result = await entitlement_service.can_use_feature(
        organization_id=10,
        feature_key="max_users",
        amount=1,
    )

    assert result["allowed"] is False
    assert result["reason"] == "Feature usage limit exceeded"
    assert result["remaining"] == 0


@pytest.mark.asyncio
async def test_can_use_feature_allows_unlimited_feature():
    entitlement_service = EntitlementDomainService(
        subscription_service=FakeSubscriptionService(
            subscription=FakeSubscription(status="active")
        ),
        plan_limit_service=FakePlanLimitService(
            plan_limit=FakePlanLimit(limit_value=None, is_unlimited=True)
        ),
        feature_usage_service=FakeFeatureUsageService(
            usage=FakeFeatureUsage(used_value=100)
        ),
    )

    result = await entitlement_service.can_use_feature(
        organization_id=10,
        feature_key="storage",
        amount=50,
    )

    assert result["allowed"] is True
    assert result["reason"] is None
    assert result["remaining"] == -1


@pytest.mark.asyncio
async def test_can_use_feature_treats_missing_usage_as_zero():
    entitlement_service = EntitlementDomainService(
        subscription_service=FakeSubscriptionService(
            subscription=FakeSubscription(status="active")
        ),
        plan_limit_service=FakePlanLimitService(
            plan_limit=FakePlanLimit(limit_value=10, is_unlimited=False)
        ),
        feature_usage_service=FakeFeatureUsageService(usage=None),
    )

    result = await entitlement_service.can_use_feature(
        organization_id=10,
        feature_key="max_users",
        amount=1,
    )

    assert result["allowed"] is True
    assert result["reason"] is None
    assert result["remaining"] == 9


@pytest.mark.asyncio
async def test_can_use_feature_denies_when_no_active_subscription_exists():
    entitlement_service = EntitlementDomainService(
        subscription_service=FakeSubscriptionService(subscription=None),
        plan_limit_service=FakePlanLimitService(
            plan_limit=FakePlanLimit(limit_value=10, is_unlimited=False)
        ),
        feature_usage_service=FakeFeatureUsageService(
            usage=FakeFeatureUsage(used_value=5)
        ),
    )

    result = await entitlement_service.can_use_feature(
        organization_id=10,
        feature_key="max_users",
        amount=1,
    )

    assert result["allowed"] is False
    assert result["reason"] == "No active subscription found"
    assert result["remaining"] == 0


@pytest.mark.asyncio
async def test_can_use_feature_denies_when_subscription_is_expired():
    entitlement_service = EntitlementDomainService(
        subscription_service=FakeSubscriptionService(
            subscription=FakeSubscription(status="expired")
        ),
        plan_limit_service=FakePlanLimitService(
            plan_limit=FakePlanLimit(limit_value=10, is_unlimited=False)
        ),
        feature_usage_service=FakeFeatureUsageService(
            usage=FakeFeatureUsage(used_value=5)
        ),
    )

    result = await entitlement_service.can_use_feature(
        organization_id=10,
        feature_key="max_users",
        amount=1,
    )

    assert result["allowed"] is False
    assert result["reason"] == "Subscription status is expired"
    assert result["remaining"] == 0


@pytest.mark.asyncio
async def test_can_use_feature_denies_when_subscription_is_past_due():
    entitlement_service = EntitlementDomainService(
        subscription_service=FakeSubscriptionService(
            subscription=FakeSubscription(status="past_due")
        ),
        plan_limit_service=FakePlanLimitService(
            plan_limit=FakePlanLimit(limit_value=10, is_unlimited=False)
        ),
        feature_usage_service=FakeFeatureUsageService(
            usage=FakeFeatureUsage(used_value=5)
        ),
    )

    result = await entitlement_service.can_use_feature(
        organization_id=10,
        feature_key="max_users",
        amount=1,
    )

    assert result["allowed"] is False
    assert result["reason"] == "Subscription status is past_due"
    assert result["remaining"] == 0


@pytest.mark.asyncio
async def test_can_use_feature_denies_when_plan_limit_missing():
    entitlement_service = EntitlementDomainService(
        subscription_service=FakeSubscriptionService(
            subscription=FakeSubscription(status="active")
        ),
        plan_limit_service=FakePlanLimitService(plan_limit=None),
        feature_usage_service=FakeFeatureUsageService(
            usage=FakeFeatureUsage(used_value=5)
        ),
    )

    result = await entitlement_service.can_use_feature(
        organization_id=10,
        feature_key="max_users",
        amount=1,
    )

    assert result["allowed"] is False
    assert result["reason"] == "Feature limit not configured"
    assert result["remaining"] == 0


@pytest.mark.asyncio
async def test_can_use_feature_allows_when_subscription_is_trialing():
    entitlement_service = EntitlementDomainService(
        subscription_service=FakeSubscriptionService(
            subscription=FakeSubscription(status="trialing")
        ),
        plan_limit_service=FakePlanLimitService(
            plan_limit=FakePlanLimit(limit_value=10, is_unlimited=False)
        ),
        feature_usage_service=FakeFeatureUsageService(
            usage=FakeFeatureUsage(used_value=5)
        ),
    )

    result = await entitlement_service.can_use_feature(
        organization_id=10,
        feature_key="max_users",
        amount=1,
    )

    assert result["allowed"] is True
    assert result["reason"] is None
    assert result["remaining"] == 4
