from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def organization_onboarding_domain_service():
    from src.modules.organization.domain.services.organization_onboarding_domain_service import (
        OrganizationOnboardingDomainService,
    )

    mock_repo = AsyncMock()
    mock_repo.get_by = AsyncMock()
    mock_repo.add = AsyncMock()
    return OrganizationOnboardingDomainService(repository=mock_repo)


def _make_onboarding(**overrides):
    from src.modules.organization.domain.entities.organization_onboarding_entity import (
        OrganizationOnboardingEntity,
    )

    data = {
        "organization_id": 1,
        "size_range": "11-50",
        "use_case": ["team collaboration"],
    }
    data.update(overrides)
    return OrganizationOnboardingEntity(**data)


@pytest.mark.asyncio
async def test_create_onboarding_success(
    organization_onboarding_domain_service,
):
    onboarding = _make_onboarding()

    organization_onboarding_domain_service.repository.get_by = AsyncMock(
        return_value=None
    )
    organization_onboarding_domain_service.repository.add = AsyncMock(
        return_value=onboarding
    )

    created = (
        await organization_onboarding_domain_service.create_organization_onboarding(
            onboarding
        )
    )

    assert created == onboarding
    organization_onboarding_domain_service.repository.get_by.assert_awaited_once_with(
        organization_id=1
    )
    organization_onboarding_domain_service.repository.add.assert_awaited_once_with(
        onboarding
    )


@pytest.mark.asyncio
async def test_create_onboarding_with_existing_record_raises_conflict(
    organization_onboarding_domain_service,
):
    from src.shared.exceptions.base_exceptions import ConflictError

    existing = _make_onboarding()
    organization_onboarding_domain_service.repository.get_by = AsyncMock(
        return_value=existing
    )

    with pytest.raises(ConflictError):
        await organization_onboarding_domain_service.create_organization_onboarding(
            _make_onboarding()
        )

    organization_onboarding_domain_service.repository.add.assert_not_called()


@pytest.mark.asyncio
async def test_create_onboarding_wraps_unexpected_error(
    organization_onboarding_domain_service,
):
    from src.shared.exceptions.base_exceptions import CreateError

    organization_onboarding_domain_service.repository.get_by = AsyncMock(
        side_effect=ValueError("unexpected")
    )

    with pytest.raises(CreateError):
        await organization_onboarding_domain_service.create_organization_onboarding(
            _make_onboarding()
        )


@pytest.mark.asyncio
async def test_create_onboarding_re_raises_domain_error(
    organization_onboarding_domain_service,
):
    from src.shared.exceptions.base_exceptions import DomainError

    organization_onboarding_domain_service.repository.get_by = AsyncMock(
        side_effect=DomainError(error="domain error")
    )

    with pytest.raises(DomainError):
        await organization_onboarding_domain_service.create_organization_onboarding(
            _make_onboarding()
        )
