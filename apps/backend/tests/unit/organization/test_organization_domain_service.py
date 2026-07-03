from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def organization_domain_service():
    from src.modules.organization.domain.services.organization_domain_service import (
        OrganizationDomainService,
    )

    mock_repo = AsyncMock()
    mock_repo.get_by = AsyncMock()
    mock_repo.add = AsyncMock()
    return OrganizationDomainService(repository=mock_repo)


@pytest.mark.asyncio
async def test_create_organization_with_existing_slug_raises_conflict(
    organization_domain_service,
):
    from src.modules.organization.domain.entities.organization_entity import (
        OrganizationEntity,
    )
    from src.shared.exceptions.base_exceptions import ConflictError

    organization_domain_service.repository.get_by = AsyncMock(
        side_effect=[
            OrganizationEntity(
                name="Acme", type="startup", slug="acme", domain="acme.com", owner_id=1
            )
        ]
    )

    with pytest.raises(ConflictError):
        await organization_domain_service.create_organization(
            OrganizationEntity(
                name="Acme",
                description=None,
                type="startup",
                slug="acme",
                logo=None,
                domain="acme.com",
                owner_id=1,
            )
        )


@pytest.mark.asyncio
async def test_create_organization_success(organization_domain_service):
    from src.modules.organization.domain.entities.organization_entity import (
        OrganizationEntity,
    )

    org = OrganizationEntity(
        name="Acme",
        description="desc",
        type="startup",
        slug="acme",
        logo=None,
        domain="acme.com",
        owner_id=1,
    )

    organization_domain_service.repository.get_by = AsyncMock(side_effect=[None, None])
    organization_domain_service.repository.add = AsyncMock(return_value=org)

    created = await organization_domain_service.create_organization(org)
    assert created == org
