import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.billing.domain.entities.billing_plan_entity import BillingPlanEntity
from src.modules.billing.domain.repositories.billing_plan_repository import (
    IBillingPlanRepository,
)
from src.modules.billing.domain.services.billing_plan_domain_service import (
    BillingPlanDomainService,
)
from src.shared.exceptions.base_exceptions import ConflictError


class FakeBillingPlanRepository(IBillingPlanRepository):
    def __init__(self, session: AsyncSession | None = None):
        self.session = session
        self.items: list[BillingPlanEntity] = []

    async def add(self, entity: BillingPlanEntity, *, audit: bool = True):
        entity.id = len(self.items) + 1
        self.items.append(entity)
        return entity

    async def get_by_id(self, entity_id: int) -> BillingPlanEntity | None:
        for item in self.items:
            if item.id == entity_id:
                return item
        return None

    async def get_by_uuid(self, entity_uuid: str) -> BillingPlanEntity | None:
        for item in self.items:
            if item.uuid == entity_uuid:
                return item
        return None

    async def get_by(self, **criteria):
        for item in self.items:
            if all(getattr(item, key) == value for key, value in criteria.items()):
                return item
        return None

    async def update(
        self,
        entity: BillingPlanEntity,
        *,
        audit: bool = True,
    ) -> BillingPlanEntity:
        if entity.id is not None:
            for index, item in enumerate(self.items):
                if item.id == entity.id:
                    self.items[index] = entity
                    return entity

        self.items.append(entity)
        return entity

    async def delete(self, entity_id: int, audit: bool = True) -> None:
        self.items = [item for item in self.items if item.id != entity_id]

    async def filter(self, **criteria):
        if not criteria:
            return self.items

        return [
            item
            for item in self.items
            if all(getattr(item, key) == value for key, value in criteria.items())
        ]


@pytest.mark.asyncio
async def test_create_billing_plan_success():
    repository = FakeBillingPlanRepository()
    service = BillingPlanDomainService(repository)

    billing_plan = BillingPlanEntity(
        name="Pro Plan",
        slug="pro-plan",
        price=20.0,
        currency="EUR",
        interval="monthly",
        is_active=True,
    )

    created_plan = await service.create_billing_plan(
        billing_plan,
        actor_id=1,
    )

    assert created_plan.id == 1
    assert created_plan.name == "Pro Plan"
    assert created_plan.slug == "pro-plan"


@pytest.mark.asyncio
async def test_create_billing_plan_duplicate_slug_raises_conflict_error():
    repository = FakeBillingPlanRepository()
    service = BillingPlanDomainService(repository)

    existing_plan = BillingPlanEntity(
        name="Pro Plan",
        slug="pro-plan",
        price=20.0,
        currency="EUR",
        interval="monthly",
        is_active=True,
    )

    await service.create_billing_plan(
        existing_plan,
        actor_id=1,
    )

    duplicate_plan = BillingPlanEntity(
        name="Another Pro Plan",
        slug="pro-plan",
        price=30.0,
        currency="EUR",
        interval="monthly",
        is_active=True,
    )

    with pytest.raises(ConflictError):
        await service.create_billing_plan(duplicate_plan, actor_id=1)


@pytest.mark.asyncio
async def test_list_billing_plans_returns_all_plans():
    repository = FakeBillingPlanRepository()
    service = BillingPlanDomainService(repository)

    await service.create_billing_plan(
        BillingPlanEntity(
            name="Free Plan",
            slug="free-plan",
            price=0.0,
            currency="EUR",
            interval="monthly",
            is_active=True,
        ),
        actor_id=1,
    )

    await service.create_billing_plan(
        BillingPlanEntity(
            name="Pro Plan",
            slug="pro-plan",
            price=20.0,
            currency="EUR",
            interval="monthly",
            is_active=True,
        ),
        actor_id=1,
    )

    plans = await service.list_billing_plan()

    assert len(plans) == 2
    assert plans[0].slug == "free-plan"
    assert plans[1].slug == "pro-plan"
