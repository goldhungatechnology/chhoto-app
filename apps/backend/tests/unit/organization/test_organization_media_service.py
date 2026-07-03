from unittest.mock import AsyncMock
import pytest
from src.modules.organization.domain.entities.organization_media_entity import (
    OrganizationMediaEntity,
)
from src.modules.organization.domain.events.organization_media_domain_events import (
    OrganizationMediaCreatedEvent,
    OrganizationMediaUpdatedEvent,
)
from src.modules.organization.domain.repositories.organization_media_repository import (
    IOrganizationMediaRepository,
)
from src.modules.organization.domain.services.organization_media_domain_service import (
    OrganizationMediaDomainService,
)
from src.shared.exceptions.base_exceptions import ConflictError, InvalidError


class FakeOrganizationMediaRepository(IOrganizationMediaRepository):
    def __init__(self):
        self.session = AsyncMock()
        self.items: list[OrganizationMediaEntity] = []

    async def add(
        self,
        entity: OrganizationMediaEntity,
        *,
        audit: bool = True,
    ) -> OrganizationMediaEntity:
        entity.id = len(self.items) + 1
        self.items.append(entity)
        return entity

    async def get_by(self, **criteria) -> OrganizationMediaEntity | None:
        for item in self.items:
            if all(getattr(item, key) == value for key, value in criteria.items()):
                return item
        return None

    async def update(
        self,
        entity: OrganizationMediaEntity,
        *,
        audit: bool = True,
    ) -> OrganizationMediaEntity:
        for index, item in enumerate(self.items):
            if item.id == entity.id:
                self.items[index] = entity
                return entity

        return entity


def _make_organization_media(**overrides):
    data = {
        "organization_id": 1,
        "whatsapp": "+358123456789",
        "linkedin": "https://www.linkedin.com/company/test",
        "created_by_id": 42,
    }
    data.update(overrides)
    return OrganizationMediaEntity(**data)


@pytest.mark.asyncio
async def test_create_organization_media_successfully():
    repository = FakeOrganizationMediaRepository()
    service = OrganizationMediaDomainService(repository)

    media = _make_organization_media()

    created_media = await service.create_organization_media(
        media_entity=media,
        actor_id=42,
    )

    assert created_media.id == 1
    assert created_media.organization_id == 1
    assert created_media.whatsapp == "+358123456789"
    assert created_media.linkedin == "https://www.linkedin.com/company/test"

    events = created_media.pull_events()

    assert len(events) == 1
    assert isinstance(events[0], OrganizationMediaCreatedEvent)
    assert events[0].actor_id == 42
    assert events[0].organization_id == 1
    assert events[0].organization_media_id == 1


@pytest.mark.asyncio
async def test_create_organization_media_raises_conflict_error_when_duplicate_exists():
    repository = FakeOrganizationMediaRepository()
    service = OrganizationMediaDomainService(repository)

    media = _make_organization_media()

    await service.create_organization_media(
        media_entity=media,
        actor_id=42,
    )

    duplicate_media = _make_organization_media(
        whatsapp="+358987654321",
        linkedin="https://www.linkedin.com/company/duplicate",
    )

    with pytest.raises(ConflictError):
        await service.create_organization_media(
            media_entity=duplicate_media,
            actor_id=42,
        )


@pytest.mark.asyncio
async def test_get_organization_media_successfully():
    repository = FakeOrganizationMediaRepository()
    service = OrganizationMediaDomainService(repository)

    media = _make_organization_media()

    await service.create_organization_media(
        media_entity=media,
        actor_id=42,
    )

    result = await service.get_organization_media(organization_id=1)

    assert result is not None
    assert result.organization_id == 1
    assert result.whatsapp == "+358123456789"
    assert result.linkedin == "https://www.linkedin.com/company/test"


@pytest.mark.asyncio
async def test_get_organization_media_returns_none_when_not_found():
    repository = FakeOrganizationMediaRepository()
    service = OrganizationMediaDomainService(repository)

    result = await service.get_organization_media(organization_id=999)

    assert result is None


@pytest.mark.asyncio
async def test_update_organization_media_successfully():
    repository = FakeOrganizationMediaRepository()
    service = OrganizationMediaDomainService(repository)

    media = _make_organization_media()

    created_media = await service.create_organization_media(
        media_entity=media,
        actor_id=42,
    )

    created_media.pull_events()

    updated_entity = OrganizationMediaEntity(
        id=created_media.id,
        uuid=created_media.uuid,
        organization_id=created_media.organization_id,
        whatsapp="+358987654321",
        linkedin="https://www.linkedin.com/company/updated",
        created_at=created_media.created_at,
        updated_at=created_media.updated_at,
        created_by_id=created_media.created_by_id,
        updated_by_id=100,
    )

    updated_media = await service.update_organization_media(
        media_entity=updated_entity,
        actor_id=100,
    )

    assert updated_media.id == created_media.id
    assert updated_media.organization_id == 1
    assert updated_media.whatsapp == "+358987654321"
    assert updated_media.linkedin == "https://www.linkedin.com/company/updated"
    assert updated_media.updated_by_id == 100

    events = updated_media.pull_events()

    assert len(events) == 1
    assert isinstance(events[0], OrganizationMediaUpdatedEvent)
    assert events[0].actor_id == 100
    assert events[0].organization_id == 1
    assert events[0].organization_media_id == created_media.id


@pytest.mark.asyncio
async def test_update_organization_media_raises_invalid_error_when_not_found():
    repository = FakeOrganizationMediaRepository()
    service = OrganizationMediaDomainService(repository)

    media = _make_organization_media(
        id=999,
        updated_by_id=42,
    )

    with pytest.raises(InvalidError):
        await service.update_organization_media(
            media_entity=media,
            actor_id=42,
        )
