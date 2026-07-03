import pytest
from typing import cast
from src.modules.billing.application.usecases.create_billing_subscription_usecase import (
    CreateBillingSubscriptionUseCase,
)
from src.modules.billing.domain.entities.billing_subscription_entity import (
    BillingSubscriptionEntity,
)
from src.modules.billing.domain.services.billing_subscription_domain_service import (
    BillingSubscriptionDomainService,
)
from src.modules.billing.presentation.schemas.billing_subscription_schemas import (
    CreateBillingSubscriptionRequestSchema,
)

from src.modules.billing.domain.repositories.billing_subscription_repository import (
    IBillingSubscriptionRepository,
)
from src.shared.exceptions.base_exceptions import ConflictError


def _matches(item, criteria: dict) -> bool:
    """
    Minimal criteria matcher mirroring the real repository's operator support
    (currently exact match and the ``__in`` membership operator).
    """
    for key, value in criteria.items():
        if key.endswith("__in"):
            if getattr(item, key[: -len("__in")]) not in value:
                return False
        elif getattr(item, key) != value:
            return False
    return True


class FakeBillingSubscriptionRepository:
    def __init__(self):
        self.items = []

    async def add(self, entity: BillingSubscriptionEntity, *, audit: bool = True):
        entity.id = len(self.items) + 1
        self.items.append(entity)
        return entity

    async def get_by(self, **criteria):
        for item in self.items:
            if _matches(item, criteria):
                return item
        return None

    async def filter(self, **criteria):
        if not criteria:
            return self.items

        return [item for item in self.items if _matches(item, criteria)]


@pytest.mark.asyncio
async def test_create_billing_subscription_usecase_success():
    repository = FakeBillingSubscriptionRepository()
    domain_service = BillingSubscriptionDomainService(
        cast(IBillingSubscriptionRepository, repository)
    )
    use_case = CreateBillingSubscriptionUseCase(domain_service)

    payload = CreateBillingSubscriptionRequestSchema(
        plan_id=1,
        billing_cycle="monthly",
        auto_renew=False,
    )

    result = await use_case.execute(
        payload=payload,
        organization_id=10,
        actor_id=1,
    )

    assert "billing_subscription_uuid" in result
    assert result["organization_id"] == "10"
    assert result["plan_id"] == "1"

    created = repository.items[0]

    # Status is derived server-side ("active"), never taken from the client.
    assert created.status == "active"
    assert created.auto_renew is False


@pytest.mark.asyncio
async def test_create_billing_subscription_blocks_duplicate_active_subscription():
    repository = FakeBillingSubscriptionRepository()
    domain_service = BillingSubscriptionDomainService(
        cast(IBillingSubscriptionRepository, repository)
    )

    subscription = BillingSubscriptionEntity(
        organization_id=10,
        plan_id=1,
        status="active",
        auto_renew=True,
        cancel_at_period_end=False,
        billing_cycle="monthly",
    )

    await domain_service.create_billing_subscription(
        billing_subscription_entity=subscription,
        actor_id=1,
    )

    duplicate_subscription = BillingSubscriptionEntity(
        organization_id=10,
        plan_id=2,
        status="active",
        auto_renew=True,
        cancel_at_period_end=False,
        billing_cycle="monthly",
    )

    with pytest.raises(ConflictError):
        await domain_service.create_billing_subscription(
            billing_subscription_entity=duplicate_subscription,
            actor_id=1,
        )


@pytest.mark.asyncio
async def test_get_active_billing_subscription_returns_active_subscription():
    repository = FakeBillingSubscriptionRepository()
    domain_service = BillingSubscriptionDomainService(
        cast(IBillingSubscriptionRepository, repository)
    )

    subscription = BillingSubscriptionEntity(
        organization_id=10,
        plan_id=1,
        status="active",
        auto_renew=True,
        cancel_at_period_end=False,
        billing_cycle="monthly",
    )

    await domain_service.create_billing_subscription(
        billing_subscription_entity=subscription,
        actor_id=1,
    )

    active_subscription = await domain_service.get_active_billing_subscription()

    assert active_subscription is not None
    assert active_subscription.status == "active"
    assert active_subscription.organization_id == 10
