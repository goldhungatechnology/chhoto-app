from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def user_onboarding_domain_service():
    from src.modules.auth.domain.services.user_onboarding_domain_service import (
        UserOnboardingDomainService,
    )

    mock_repo = AsyncMock()
    return UserOnboardingDomainService(repository=mock_repo)


@pytest.mark.asyncio
async def test_create_user_onboarding_success(user_onboarding_domain_service):
    from src.modules.auth.domain.entities.user_onboarding_entity import (
        UserOnboardingEntity,
    )

    onboarding_entity = UserOnboardingEntity(
        user_id=1,
        theme="dark",
        referral_source="social media",
    )

    user_onboarding_domain_service.repository.get_by = AsyncMock(return_value=None)
    user_onboarding_domain_service.repository.add = AsyncMock(
        return_value=onboarding_entity
    )

    result = await user_onboarding_domain_service.create_user_onboarding(
        onboarding_entity
    )

    assert result.user_id == 1
    assert result.theme == "dark"
    assert result.referral_source == "social media"
    user_onboarding_domain_service.repository.get_by.assert_awaited_once_with(user_id=1)
    user_onboarding_domain_service.repository.add.assert_awaited_once()

    events = result.pull_events()
    assert len(events) == 1
    from src.modules.auth.domain.events.auth_onboarding_domain_events import (
        UserOnboardingCompletedEvent,
    )

    assert isinstance(events[0], UserOnboardingCompletedEvent)
    assert events[0].user_id == 1


@pytest.mark.asyncio
async def test_create_user_onboarding_duplicate(user_onboarding_domain_service):
    from src.modules.auth.domain.entities.user_onboarding_entity import (
        UserOnboardingEntity,
    )
    from src.shared.exceptions.base_exceptions import ConflictError

    onboarding_entity = UserOnboardingEntity(
        user_id=1,
        theme="dark",
        referral_source="social media",
    )

    user_onboarding_domain_service.repository.get_by = AsyncMock(
        return_value=onboarding_entity
    )

    with pytest.raises(
        ConflictError, match="User onboarding already exists for this user"
    ):
        await user_onboarding_domain_service.create_user_onboarding(onboarding_entity)

    user_onboarding_domain_service.repository.add.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_user_onboarding_repository_error(user_onboarding_domain_service):
    from src.modules.auth.domain.entities.user_onboarding_entity import (
        UserOnboardingEntity,
    )
    from src.shared.exceptions.base_exceptions import CreateError

    onboarding_entity = UserOnboardingEntity(
        user_id=1,
        theme="dark",
        referral_source="social media",
    )

    user_onboarding_domain_service.repository.get_by = AsyncMock(return_value=None)
    user_onboarding_domain_service.repository.add = AsyncMock(
        side_effect=Exception("Database connection failed")
    )

    with pytest.raises(CreateError, match="Failed to create user onboarding"):
        await user_onboarding_domain_service.create_user_onboarding(onboarding_entity)
