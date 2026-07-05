from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def get_user_details_usecase():
    from src.modules.auth.application.usecases.core.get_user_details_usecase import (
        GetUserDetailsUseCase,
    )

    mock_user_domain_service = AsyncMock()
    mock_user_domain_service.get_user_by_id = AsyncMock()

    mock_user_session_domain_service = AsyncMock()
    mock_user_session_domain_service.get_user_session_by_uuid = AsyncMock()

    mock_cache_service = AsyncMock()
    mock_cache_service.is_user_online = AsyncMock()

    mock_country_reader = AsyncMock()
    mock_country_reader.get_country_by_id = AsyncMock()

    mock_user_mfa_domain_service = AsyncMock()
    mock_user_mfa_domain_service.is_mfa_required = AsyncMock(return_value=False)

    return GetUserDetailsUseCase(
        user_domain_service=mock_user_domain_service,
        user_onboarding_domain_service=AsyncMock(),
        user_account_domain_service=AsyncMock(),
        user_session_domain_service=mock_user_session_domain_service,
        cache_service=mock_cache_service,
        country_reader=mock_country_reader,
        user_mfa_domain_service=mock_user_mfa_domain_service,
    )


def _make_user(**overrides):
    from src.modules.auth.domain.entities.user_entity import UserEntity

    data = {
        "id": 1,
        "uuid": "user-uuid-123",
        "username": "testuser",
        "email": "test@example.com",
        "avatar_bg": "#ffffff",
        "status": "active",
        "is_onboarded": True,
    }
    data.update(overrides)
    return UserEntity(**data)


@pytest.mark.asyncio
async def test_execute_returns_user_details_successfully(
    get_user_details_usecase,
):
    user = _make_user()

    get_user_details_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=user
    )
    get_user_details_usecase.cache_service.is_user_online = AsyncMock(return_value=True)
    get_user_details_usecase.user_onboarding_domain_service.get_user_onboarding_by_user_id = AsyncMock(
        return_value=None
    )

    (
        user_result,
        onboarding_details,
        orgs_result,
        is_online,
        last_org,
        country,
        user_account,
        _mfa_enabled,
    ) = await get_user_details_usecase.execute(
        user_id=1, session_uuid="test-session-uuid"
    )

    assert user_result == user
    assert orgs_result is None
    assert is_online is True
    assert last_org is None
    assert country is None

    get_user_details_usecase.user_domain_service.get_user_by_id.assert_awaited_once_with(
        1
    )
    get_user_details_usecase.cache_service.is_user_online.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_execute_returns_country_details_when_country_id_set(
    get_user_details_usecase,
):
    user = _make_user(country_id=5)
    mock_country = AsyncMock()

    get_user_details_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=user
    )
    get_user_details_usecase.country_reader.get_country_by_id = AsyncMock(
        return_value=mock_country
    )
    get_user_details_usecase.cache_service.is_user_online = AsyncMock(return_value=False)
    get_user_details_usecase.user_onboarding_domain_service.get_user_onboarding_by_user_id = AsyncMock(
        return_value=None
    )

    (
        user_result,
        onboarding_details,
        orgs_result,
        is_online,
        last_org,
        country,
        user_account,
        _mfa_enabled,
    ) = await get_user_details_usecase.execute(
        user_id=1, session_uuid="test-session-uuid"
    )

    assert user_result == user
    assert country == mock_country
    get_user_details_usecase.country_reader.get_country_by_id.assert_awaited_once_with(
        5
    )


@pytest.mark.asyncio
async def test_execute_raises_server_error_when_user_not_found(
    get_user_details_usecase,
):
    from src.shared.exceptions.base_exceptions import ServerError

    get_user_details_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=None
    )

    with pytest.raises(ServerError) as exc_info:
        await get_user_details_usecase.execute(
            user_id=1, session_uuid="test-session-uuid"
        )
    assert exc_info.value.error == "Error while retrieving user details"


@pytest.mark.asyncio
async def test_execute_raises_server_error_when_user_has_no_id(
    get_user_details_usecase,
):
    from src.shared.exceptions.base_exceptions import ServerError

    user = _make_user(id=None)
    get_user_details_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=user
    )

    with pytest.raises(ServerError) as exc_info:
        await get_user_details_usecase.execute(
            user_id=1, session_uuid="test-session-uuid"
        )
    assert exc_info.value.error == "Error while retrieving user details"


@pytest.mark.asyncio
async def test_execute_wraps_unexpected_error_in_server_error(
    get_user_details_usecase,
):
    from src.shared.exceptions.base_exceptions import ServerError

    get_user_details_usecase.user_domain_service.get_user_by_id = AsyncMock(
        side_effect=Exception("Database crash")
    )

    with pytest.raises(ServerError) as exc_info:
        await get_user_details_usecase.execute(
            user_id=1, session_uuid="test-session-uuid"
        )
    assert (
        exc_info.value.error
        == "An error occurred while retrieving user details"
    )
