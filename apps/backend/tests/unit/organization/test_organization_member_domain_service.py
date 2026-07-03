from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def organization_member_domain_service():
    from src.modules.organization.domain.services.organization_member_domain_service import (
        OrganizationMemberDomainService,
    )

    mock_repo = AsyncMock()
    mock_repo.get_by = AsyncMock()
    mock_repo.add = AsyncMock()
    return OrganizationMemberDomainService(repository=mock_repo)


@pytest.mark.asyncio
async def test_add_member_with_existing_membership_raises_conflict(
    organization_member_domain_service,
):
    from src.modules.organization.domain.entities.organization_member_entity import (
        OrganizationMemberEntity,
    )
    from src.shared.exceptions.base_exceptions import ConflictError

    existing = OrganizationMemberEntity(
        organization_id=1,
        user_id=2,
        status="active",
    )
    organization_member_domain_service.repository.get_by = AsyncMock(
        return_value=existing
    )

    with pytest.raises(ConflictError):
        await organization_member_domain_service.add_member(
            OrganizationMemberEntity(
                organization_id=1,
                user_id=2,
                status="active",
            )
        )


@pytest.mark.asyncio
async def test_add_member_success(organization_member_domain_service):
    from src.modules.organization.domain.entities.organization_member_entity import (
        OrganizationMemberEntity,
    )

    member = OrganizationMemberEntity(
        organization_id=1,
        user_id=2,
        status="active",
    )

    organization_member_domain_service.repository.get_by = AsyncMock(return_value=None)
    organization_member_domain_service.repository.add = AsyncMock(return_value=member)

    created = await organization_member_domain_service.add_member(member)
    assert created == member
