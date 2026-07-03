import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.billing.application.usecases.create_billing_plan_limit_usecase import (
    CreateBillingPlanLimitUseCase,
)
from src.modules.billing.application.usecases.list_billing_plan_limit_usecase import (
    ListBillingPlanLimitUseCase,
)
from src.modules.billing.domain.entities.billing_plan_limit_entity import (
    BillingPlanLimitEntity,
)
from src.modules.billing.domain.repositories.billing_plan_limit_repository import (
    IBillingPlanLimitRepository,
)
from src.modules.billing.domain.services.billing_plan_limit_domain_service import (
    BillingPlanLimitDomainService,
)
from src.modules.billing.presentation.schemas.billing_plan_limit_schemas import (
    CreateBillingPlanLimitRequestSchema,
)


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
async def test_create_billing_plan_limit_use_case_success():
    repository = FakeBillingPlanLimitRepository()
    domain_service = BillingPlanLimitDomainService(repository)
    use_case = CreateBillingPlanLimitUseCase(domain_service)

    payload = CreateBillingPlanLimitRequestSchema(
        plan_id=1,
        feature_key=" Max_Users ",
        limit_value=10,
        is_unlimited=False,
    )

    result = await use_case.execute(
        payload,
        actor_id=1,
    )

    assert result["feature_key"] == "max_users"
    assert "billing_plan_limit_uuid" in result


@pytest.mark.asyncio
async def test_list_billing_plan_limits_use_case_success():
    repository = FakeBillingPlanLimitRepository()
    domain_service = BillingPlanLimitDomainService(repository)

    create_use_case = CreateBillingPlanLimitUseCase(domain_service)
    list_use_case = ListBillingPlanLimitUseCase(domain_service)

    await create_use_case.execute(
        CreateBillingPlanLimitRequestSchema(
            plan_id=1,
            feature_key="max_users",
            limit_value=10,
            is_unlimited=False,
        ),
        actor_id=1,
    )

    await create_use_case.execute(
        CreateBillingPlanLimitRequestSchema(
            plan_id=1,
            feature_key="max_uploads",
            limit_value=100,
            is_unlimited=False,
        ),
        actor_id=1,
    )

    await create_use_case.execute(
        CreateBillingPlanLimitRequestSchema(
            plan_id=2,
            feature_key="max_users",
            limit_value=20,
            is_unlimited=False,
        ),
        actor_id=1,
    )

    result = await list_use_case.execute(plan_id=1)

    assert len(result) == 2
    assert result[0]["plan_id"] == 1
    assert result[1]["plan_id"] == 1
