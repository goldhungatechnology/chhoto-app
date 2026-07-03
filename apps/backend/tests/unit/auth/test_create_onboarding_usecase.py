from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def create_onboarding_usecase():
    from src.modules.auth.application.usecases.onboarding.create_onboarding_usecase import (
        CreateOnboardingUseCase,
    )

    mock_onboarding_service = AsyncMock()
    mock_user_service = AsyncMock()
    return CreateOnboardingUseCase(
        user_onboarding_domain_service=mock_onboarding_service,
        user_domain_service=mock_user_service,
    )


@pytest.mark.asyncio
async def test_execute_onboarding_success(create_onboarding_usecase):
    from src.modules.auth.domain.entities.user_entity import UserEntity
    from src.modules.auth.domain.entities.user_onboarding_entity import (
        UserOnboardingEntity,
    )
    from src.modules.auth.domain.events.auth_domain_events import UserUpdatedEvent
    from src.modules.auth.domain.events.auth_onboarding_domain_events import (
        UserOnboardingCompletedEvent,
    )
    from src.modules.auth.presentation.schemas.auth_onboarding_schemas import (
        OnboardingRequestSchema,
    )

    payload = OnboardingRequestSchema(
        theme="light",
        referral_source="friend referral",
    )

    created_entity = UserOnboardingEntity(
        id=1,
        user_id=42,
        theme="light",
        referral_source="friend referral",
        created_at=datetime.now(UTC),
    )
    created_entity.add_event(
        UserOnboardingCompletedEvent(
            user_id=42,
            theme="light",
            referral_source="friend referral",
        )
    )

    updated_user = UserEntity(
        id=42,
        username="testuser",
        email="test@example.com",
        avatar_bg="#ffffff",
        status="active",
        is_onboarded=True,
    )
    updated_user.add_event(UserUpdatedEvent(user_id=42))

    create_onboarding_usecase.user_onboarding_domain_service.create_user_onboarding = (
        AsyncMock(return_value=created_entity)
    )
    create_onboarding_usecase.user_domain_service.mark_onboarded = AsyncMock(
        return_value=updated_user
    )

    with patch(
        "src.modules.auth.application.usecases.onboarding.create_onboarding_usecase.mediator"
    ) as mock_mediator:
        mock_mediator.publish = AsyncMock()
        result = await create_onboarding_usecase.execute(payload=payload, user_id=42)

    assert result.user_id == 42
    assert result.theme == "light"
    assert result.referral_source == "friend referral"

    create_onboarding_usecase.user_onboarding_domain_service.create_user_onboarding.assert_awaited_once()
    create_onboarding_usecase.user_domain_service.mark_onboarded.assert_awaited_once_with(
        user_id=42
    )

    assert mock_mediator.publish.await_count == 2
    first_call_args = mock_mediator.publish.await_args_list[0][0][0]
    second_call_args = mock_mediator.publish.await_args_list[1][0][0]
    assert isinstance(first_call_args, UserOnboardingCompletedEvent)
    assert isinstance(second_call_args, UserUpdatedEvent)
