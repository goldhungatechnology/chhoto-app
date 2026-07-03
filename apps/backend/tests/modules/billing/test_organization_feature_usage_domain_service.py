import pytest

from src.modules.billing.domain.entities.organization_feature_usage_entity import (
    OrganizationFeatureUsageEntity,
)
from src.modules.billing.domain.services.organization_feature_usage_domain_service import (
    OrganizationFeatureUsageDomainService,
)
from src.shared.exceptions.base_exceptions import ConflictError

from src.modules.billing.domain.repositories.organization_feature_usage_repository import (
    IOrganizationFeatureUsageRepository,
)


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
async def test_create_organization_feature_usage_success():
    repository = FakeOrganizationFeatureUsageRepository()
    service = OrganizationFeatureUsageDomainService(repository)

    feature_usage = OrganizationFeatureUsageEntity(
        organization_id=10,
        subscription_id=1,
        feature_key="max_users",
        used_value=5,
    )

    created_usage = await service.create_organization_feature_usage(
        feature_usage,
        actor_id=1,
    )

    assert created_usage.id == 1
    assert created_usage.organization_id == 10
    assert created_usage.subscription_id == 1
    assert created_usage.feature_key == "max_users"
    assert created_usage.used_value == 5


@pytest.mark.asyncio
async def test_duplicate_feature_usage_raises_conflict_error():
    repository = FakeOrganizationFeatureUsageRepository()
    service = OrganizationFeatureUsageDomainService(repository)

    existing_usage = OrganizationFeatureUsageEntity(
        organization_id=10,
        subscription_id=1,
        feature_key="max_users",
        used_value=5,
    )

    await service.create_organization_feature_usage(
        existing_usage,
        actor_id=1,
    )

    duplicate_usage = OrganizationFeatureUsageEntity(
        organization_id=10,
        subscription_id=1,
        feature_key="max_users",
        used_value=6,
    )

    with pytest.raises(ConflictError):
        await service.create_organization_feature_usage(
            duplicate_usage,
            actor_id=1,
        )


@pytest.mark.asyncio
async def test_list_organization_feature_usage_returns_subscription_usages():
    repository = FakeOrganizationFeatureUsageRepository()
    service = OrganizationFeatureUsageDomainService(repository)

    await service.create_organization_feature_usage(
        OrganizationFeatureUsageEntity(
            organization_id=10,
            subscription_id=1,
            feature_key="max_users",
            used_value=5,
        ),
        actor_id=1,
    )

    await service.create_organization_feature_usage(
        OrganizationFeatureUsageEntity(
            organization_id=10,
            subscription_id=1,
            feature_key="max_uploads",
            used_value=20,
        ),
        actor_id=1,
    )

    usages = await service.list_organization_feature_usage(subscription_id=1)

    assert len(usages) == 2
    assert usages[0].subscription_id == 1
    assert usages[1].subscription_id == 1


@pytest.mark.asyncio
async def test_get_usage_returns_feature_usage():
    repository = FakeOrganizationFeatureUsageRepository()
    service = OrganizationFeatureUsageDomainService(repository)

    await service.create_organization_feature_usage(
        OrganizationFeatureUsageEntity(
            organization_id=10,
            subscription_id=1,
            feature_key="max_users",
            used_value=5,
        ),
        actor_id=1,
    )

    usage = await service.get_usage(
        subscription_id=1,
        feature_key="max_users",
    )

    assert usage is not None
    assert usage.used_value == 5


@pytest.mark.asyncio
async def test_increment_usage_increases_used_value():
    repository = FakeOrganizationFeatureUsageRepository()
    service = OrganizationFeatureUsageDomainService(repository)

    await service.create_organization_feature_usage(
        OrganizationFeatureUsageEntity(
            organization_id=10,
            subscription_id=1,
            feature_key="max_users",
            used_value=5,
        ),
        actor_id=1,
    )

    updated_usage = await service.increment_usage(
        subscription_id=1,
        feature_key="max_users",
        amount=2,
    )

    assert updated_usage.used_value == 7


@pytest.mark.asyncio
async def test_reset_usage_sets_all_subscription_usage_to_zero():
    repository = FakeOrganizationFeatureUsageRepository()
    service = OrganizationFeatureUsageDomainService(repository)

    await service.create_organization_feature_usage(
        OrganizationFeatureUsageEntity(
            organization_id=10,
            subscription_id=1,
            feature_key="max_users",
            used_value=5,
        ),
        actor_id=1,
    )

    await service.create_organization_feature_usage(
        OrganizationFeatureUsageEntity(
            organization_id=10,
            subscription_id=1,
            feature_key="max_uploads",
            used_value=20,
        ),
        actor_id=1,
    )

    reset_usages = await service.reset_usage(subscription_id=1)

    assert len(reset_usages) == 2
    assert reset_usages[0].used_value == 0
    assert reset_usages[1].used_value == 0
