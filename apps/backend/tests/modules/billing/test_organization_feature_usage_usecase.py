import pytest

from src.modules.billing.application.usecases.create_organization_feature_usage_usecase import (
    CreateOrganizationFeatureUsageUseCase,
)
from src.modules.billing.application.usecases.list_organization_feature_usage_usecase import (
    ListOrganizationFeatureUsageUseCase,
)
from src.modules.billing.domain.entities.organization_feature_usage_entity import (
    OrganizationFeatureUsageEntity,
)
from src.modules.billing.domain.services.organization_feature_usage_domain_service import (
    OrganizationFeatureUsageDomainService,
)
from src.modules.billing.presentation.schemas.organization_feature_usage_schemas import (
    CreateOrganizationFeatureUsageRequestSchema,
)

from src.modules.billing.domain.repositories.organization_feature_usage_repository import (
    IOrganizationFeatureUsageRepository,
)

from src.shared.mediator.mediator import mediator


class FakeOrganizationFeatureUsageRepository(IOrganizationFeatureUsageRepository):
    def __init__(self):
        self.items: list[OrganizationFeatureUsageEntity] = []

    async def add(
        self,
        entity: OrganizationFeatureUsageEntity,
        *,
        audit: bool = True,
    ):
        entity.id = len(self.items) + 1
        self.items.append(entity)
        return entity

    async def get_by_id(
        self,
        entity_id: int,
    ) -> OrganizationFeatureUsageEntity | None:
        for item in self.items:
            if item.id == entity_id:
                return item
        return None

    async def get_by_uuid(
        self,
        entity_uuid: str,
    ) -> OrganizationFeatureUsageEntity | None:
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
        entity: OrganizationFeatureUsageEntity,
        *,
        audit: bool = True,
    ) -> OrganizationFeatureUsageEntity:
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

    async def get_usage(
        self,
        subscription_id: int,
        feature_key: str,
    ) -> OrganizationFeatureUsageEntity | None:
        return await self.get_by(
            subscription_id=subscription_id,
            feature_key=feature_key.strip().lower(),
        )

    async def increment_usage(
        self,
        subscription_id: int,
        feature_key: str,
        amount: int,
    ) -> OrganizationFeatureUsageEntity:
        feature_usage = await self.get_usage(
            subscription_id=subscription_id,
            feature_key=feature_key,
        )

        if feature_usage is None:
            raise ValueError("Feature usage not found")

        feature_usage.update_used_value(feature_usage.used_value + amount)

        return await self.update(feature_usage)

    async def reset_usage(
        self,
        subscription_id: int,
    ) -> list[OrganizationFeatureUsageEntity]:
        feature_usages = await self.filter(subscription_id=subscription_id)

        reset_feature_usages = []

        for feature_usage in feature_usages:
            feature_usage.update_used_value(0)
            updated_feature_usage = await self.update(feature_usage)
            reset_feature_usages.append(updated_feature_usage)

        return reset_feature_usages


@pytest.mark.asyncio
async def test_create_organization_feature_usage_usecase_success(monkeypatch):
    async def fake_publish(event):
        return None

    monkeypatch.setattr(mediator, "publish", fake_publish)

    repository = FakeOrganizationFeatureUsageRepository()
    domain_service = OrganizationFeatureUsageDomainService(repository)
    use_case = CreateOrganizationFeatureUsageUseCase(domain_service)

    payload = CreateOrganizationFeatureUsageRequestSchema(
        subscription_id=1,
        feature_key=" Max_Users ",
        used_value=5,
    )

    result = await use_case.execute(
        payload=payload,
        organization_id=10,
        actor_id=1,
    )

    assert "organization_feature_usage_uuid" in result
    assert result["feature_key"] == "max_users"
    assert result["used_value"] == 5

    created_usage = repository.items[0]
    assert created_usage.organization_id == 10
    assert created_usage.subscription_id == 1
    assert created_usage.feature_key == "max_users"


@pytest.mark.asyncio
async def test_list_organization_feature_usage_usecase_success(monkeypatch):
    async def fake_publish(event):
        return None

    monkeypatch.setattr(mediator, "publish", fake_publish)

    repository = FakeOrganizationFeatureUsageRepository()
    domain_service = OrganizationFeatureUsageDomainService(repository)

    create_use_case = CreateOrganizationFeatureUsageUseCase(domain_service)
    list_use_case = ListOrganizationFeatureUsageUseCase(domain_service)

    await create_use_case.execute(
        CreateOrganizationFeatureUsageRequestSchema(
            subscription_id=1,
            feature_key="max_users",
            used_value=5,
        ),
        organization_id=10,
        actor_id=1,
    )

    await create_use_case.execute(
        CreateOrganizationFeatureUsageRequestSchema(
            subscription_id=1,
            feature_key="max_uploads",
            used_value=20,
        ),
        organization_id=10,
        actor_id=1,
    )

    await create_use_case.execute(
        CreateOrganizationFeatureUsageRequestSchema(
            subscription_id=2,
            feature_key="max_users",
            used_value=8,
        ),
        organization_id=10,
        actor_id=1,
    )

    result = await list_use_case.execute(subscription_id=1)

    assert len(result) == 2
    assert result[0]["subscription_id"] == 1
    assert result[1]["subscription_id"] == 1
    assert result[0]["feature_key"] == "max_users"
    assert result[1]["feature_key"] == "max_uploads"
