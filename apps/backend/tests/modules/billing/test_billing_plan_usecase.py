import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.billing.application.usecases.create_billing_plan_usecase import (
    CreateBillingPlanUseCase,
)
from src.modules.billing.application.usecases.list_billing_plan_usecase import (
    ListBillingPlanUseCase,
)
from src.modules.billing.domain.entities.billing_plan_entity import BillingPlanEntity
from src.modules.billing.domain.repositories.billing_plan_repository import (
    IBillingPlanRepository,
)
from src.modules.billing.domain.services.billing_plan_domain_service import (
    BillingPlanDomainService,
)
from src.modules.billing.presentation.schemas.billing_plan_schemas import (
    CreateBillingPlanRequestSchema,
)


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
async def test_create_billing_plan_usecase_success():
    repository = FakeBillingPlanRepository()
    domain_service = BillingPlanDomainService(repository)
    use_case = CreateBillingPlanUseCase(domain_service)

    payload = CreateBillingPlanRequestSchema(
        name="Pro Plan",
        price=20.0,
        currency="eur",
        interval="monthly",
        is_active=True,
    )

    result = await use_case.execute(
        payload,
        actor_id=1,
    )

    assert result["billing_plan_slug"] == "pro-plan"
    assert "billing_plan_uuid" in result


@pytest.mark.asyncio
async def test_list_billing_plans_use_case_success():
    repository = FakeBillingPlanRepository()
    domain_service = BillingPlanDomainService(repository)

    create_use_case = CreateBillingPlanUseCase(domain_service)
    list_use_case = ListBillingPlanUseCase(domain_service)

    await create_use_case.execute(
        CreateBillingPlanRequestSchema(
            name="Free Plan",
            price=0.0,
            currency="EUR",
            interval="monthly",
            is_active=True,
        ),
        actor_id=1,
    )

    await create_use_case.execute(
        CreateBillingPlanRequestSchema(
            name="Pro Plan",
            price=20.0,
            currency="EUR",
            interval="monthly",
            is_active=True,
        ),
        actor_id=1,
    )

    result = await list_use_case.execute()

    assert len(result) == 2
    assert result[0]["slug"] == "free-plan"
    assert result[1]["slug"] == "pro-plan"
