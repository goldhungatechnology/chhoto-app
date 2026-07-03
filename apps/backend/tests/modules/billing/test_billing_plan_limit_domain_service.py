import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.billing.domain.entities.billing_plan_limit_entity import (
    BillingPlanLimitEntity,
)
from src.modules.billing.domain.repositories.billing_plan_limit_repository import (
    IBillingPlanLimitRepository,
)
from src.modules.billing.domain.services.billing_plan_limit_domain_service import (
    BillingPlanLimitDomainService,
)
from src.shared.exceptions.base_exceptions import ConflictError


class FakeBillingPlanLimitRepository(IBillingPlanLimitRepository):
    def __init__(self, session: AsyncSession | None = None):
        self.session = session
        self.items: list[BillingPlanLimitEntity] = []

    async def add(self, entity: BillingPlanLimitEntity, *, audit: bool = True):
        entity.id = len(self.items) + 1
        self.items.append(entity)
        return entity

    async def get_by_id(self, entity_id: int) -> BillingPlanLimitEntity | None:
        for item in self.items:
            if item.id == entity_id:
                return item
        return None

    async def get_by_uuid(self, entity_uuid: str) -> BillingPlanLimitEntity | None:
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
        entity: BillingPlanLimitEntity,
        *,
        audit: bool = True,
    ) -> BillingPlanLimitEntity:
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
async def test_create_billing_plan_limit_success():
    repository = FakeBillingPlanLimitRepository()
    service = BillingPlanLimitDomainService(repository)

    billing_plan_limit = BillingPlanLimitEntity(
        plan_id=1,
        feature_key="max_users",
        limit_value=10,
        is_unlimited=False,
    )

    created_limit = await service.create_billing_plan_limit(
        billing_plan_limit,
        actor_id=1,
    )

    assert created_limit.id == 1
    assert created_limit.plan_id == 1
    assert created_limit.feature_key == "max_users"
    assert created_limit.limit_value == 10


@pytest.mark.asyncio
async def test_duplicate_feature_key_for_same_plan_raises_conflict_error():
    repository = FakeBillingPlanLimitRepository()
    service = BillingPlanLimitDomainService(repository)

    existing_limit = BillingPlanLimitEntity(
        plan_id=1,
        feature_key="max_users",
        limit_value=10,
        is_unlimited=False,
    )

    await service.create_billing_plan_limit(
        existing_limit,
        actor_id=1,
    )

    duplicate_limit = BillingPlanLimitEntity(
        plan_id=1,
        feature_key="max_users",
        limit_value=20,
        is_unlimited=False,
    )

    with pytest.raises(ConflictError):
        await service.create_billing_plan_limit(duplicate_limit, actor_id=1)


@pytest.mark.asyncio
async def test_same_feature_key_allowed_for_different_plan():
    repository = FakeBillingPlanLimitRepository()
    service = BillingPlanLimitDomainService(repository)

    await service.create_billing_plan_limit(
        BillingPlanLimitEntity(
            plan_id=1,
            feature_key="max_users",
            limit_value=10,
            is_unlimited=False,
        ),
        actor_id=1,
    )

    created_limit = await service.create_billing_plan_limit(
        BillingPlanLimitEntity(
            plan_id=2,
            feature_key="max_users",
            limit_value=20,
            is_unlimited=False,
        ),
        actor_id=1,
    )

    assert created_limit.id == 2
    assert created_limit.plan_id == 2
    assert created_limit.feature_key == "max_users"


@pytest.mark.asyncio
async def test_list_billing_plan_limits_returns_limits_for_specific_plan():
    repository = FakeBillingPlanLimitRepository()
    service = BillingPlanLimitDomainService(repository)

    await service.create_billing_plan_limit(
        BillingPlanLimitEntity(
            plan_id=1,
            feature_key="max_users",
            limit_value=10,
            is_unlimited=False,
        ),
        actor_id=1,
    )

    await service.create_billing_plan_limit(
        BillingPlanLimitEntity(
            plan_id=1,
            feature_key="max_uploads",
            limit_value=100,
            is_unlimited=False,
        ),
        actor_id=1,
    )

    await service.create_billing_plan_limit(
        BillingPlanLimitEntity(
            plan_id=2,
            feature_key="max_users",
            limit_value=20,
            is_unlimited=False,
        ),
        actor_id=1,
    )

    limits = await service.list_billing_plan_limit(plan_id=1)

    assert len(limits) == 2
    assert limits[0].plan_id == 1
    assert limits[1].plan_id == 1
