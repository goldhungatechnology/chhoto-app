from datetime import datetime, timedelta, timezone
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

    mock_organization_reader = AsyncMock()
    mock_organization_reader.get_organizations_by_user_id = AsyncMock()
    mock_organization_reader.get_organization_by_uuid = AsyncMock()

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
        organization_reader=mock_organization_reader,
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


def _make_organization(**overrides):
    from src.modules.organization.domain.entities.organization_entity import (
        OrganizationEntity,
    )

    data = {
        "id": 10,
        "uuid": "org-uuid-456",
        "name": "Test Org",
        "type": "external",
        "slug": "test-org",
        "domain": "example.com",
        "owner_id": 1,
        "logo": "https://logo.example.com/logo.png",
    }
    data.update(overrides)
    return OrganizationEntity(**data)


def _make_session(**overrides):
    from src.modules.auth.domain.entities.user_session_entity import (
        UserSessionEntity,
    )

    data = {
        "user_id": 1,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
    }
    data.update(overrides)
    return UserSessionEntity(**data)


@pytest.mark.asyncio
async def test_execute_returns_user_details_successfully(
    get_user_details_usecase,
):
    user = _make_user()
    org = _make_organization()
    organizations_list = [org]
    session = _make_session(organization_uuid=org.uuid)

    get_user_details_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=user
    )
    get_user_details_usecase.organization_reader.get_organizations_by_user_id = (
        AsyncMock(return_value=organizations_list)
    )
    get_user_details_usecase.user_session_domain_service.get_user_session_by_uuid = (
        AsyncMock(return_value=session)
    )
    get_user_details_usecase.organization_reader.get_organization_by_uuid = AsyncMock(
        return_value=org
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
    assert orgs_result == organizations_list
    assert is_online is True
    assert last_org == org
    # user has no country_id, so country is None and reader is never called
    assert country is None
    get_user_details_usecase.country_reader.get_country_by_id.assert_not_called()

    get_user_details_usecase.user_domain_service.get_user_by_id.assert_awaited_once_with(
        1
    )
    get_user_details_usecase.organization_reader.get_organizations_by_user_id.assert_awaited_once_with(
        1
    )
    get_user_details_usecase.user_session_domain_service.get_user_session_by_uuid.assert_awaited_once_with(
        "test-session-uuid"
    )
    get_user_details_usecase.organization_reader.get_organization_by_uuid.assert_awaited_once_with(
        org.uuid
    )
    get_user_details_usecase.cache_service.is_user_online.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_execute_uses_first_org_when_session_has_no_org(
    get_user_details_usecase,
):
    user = _make_user()
    org = _make_organization()
    organizations_list = [org]
    session = _make_session()

    get_user_details_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=user
    )
    get_user_details_usecase.organization_reader.get_organizations_by_user_id = (
        AsyncMock(return_value=organizations_list)
    )
    get_user_details_usecase.user_session_domain_service.get_user_session_by_uuid = (
        AsyncMock(return_value=session)
    )
    get_user_details_usecase.cache_service.is_user_online = AsyncMock(
        return_value=False
    )
    get_user_details_usecase.user_onboarding_domain_service.get_user_onboarding_by_user_id = AsyncMock(
        return_value=None
    )

    (
        _result,
        _onboarding,
        _orgs,
        is_online,
        last_org,
        _country,
        _user_account,
        _mfa_enabled,
    ) = await get_user_details_usecase.execute(
        user_id=1, session_uuid="test-session-uuid"
    )

    assert last_org == org
    assert is_online is False
    get_user_details_usecase.organization_reader.get_organization_by_uuid.assert_not_called()


@pytest.mark.asyncio
async def test_execute_returns_country_details_when_country_id_set(
    get_user_details_usecase,
):
    user = _make_user(country_id=5)
    org = _make_organization()
    session = _make_session(organization_uuid=org.uuid)
    country = object()

    get_user_details_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=user
    )
    get_user_details_usecase.organization_reader.get_organizations_by_user_id = (
        AsyncMock(return_value=[org])
    )
    get_user_details_usecase.user_session_domain_service.get_user_session_by_uuid = (
        AsyncMock(return_value=session)
    )
    get_user_details_usecase.organization_reader.get_organization_by_uuid = AsyncMock(
        return_value=org
    )
    get_user_details_usecase.cache_service.is_user_online = AsyncMock(return_value=True)
    get_user_details_usecase.user_onboarding_domain_service.get_user_onboarding_by_user_id = AsyncMock(
        return_value=None
    )
    get_user_details_usecase.country_reader.get_country_by_id = AsyncMock(
        return_value=country
    )

    (
        _user_result,
        _onboarding,
        _orgs,
        _is_online,
        _last_org,
        country_result,
        _user_account,
        _mfa_enabled,
    ) = await get_user_details_usecase.execute(
        user_id=1, session_uuid="test-session-uuid"
    )

    assert country_result is country
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

    with pytest.raises(ServerError):
        await get_user_details_usecase.execute(
            user_id=999, session_uuid="test-session-uuid"
        )


@pytest.mark.asyncio
async def test_execute_raises_server_error_when_user_has_no_id(
    get_user_details_usecase,
):
    from src.shared.exceptions.base_exceptions import ServerError

    user = _make_user(id=None)
    get_user_details_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=user
    )

    with pytest.raises(ServerError):
        await get_user_details_usecase.execute(
            user_id=999, session_uuid="test-session-uuid"
        )


@pytest.mark.asyncio
async def test_execute_raises_server_error_when_no_organizations(
    get_user_details_usecase,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    user = _make_user()
    get_user_details_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=user
    )
    get_user_details_usecase.organization_reader.get_organizations_by_user_id = (
        AsyncMock(return_value=[])
    )

    with pytest.raises(InvalidError):
        await get_user_details_usecase.execute(
            user_id=1, session_uuid="test-session-uuid"
        )


@pytest.mark.asyncio
async def test_execute_re_raises_domain_error_from_user_service(
    get_user_details_usecase,
):
    from src.shared.exceptions.base_exceptions import DomainError

    get_user_details_usecase.user_domain_service.get_user_by_id = AsyncMock(
        side_effect=DomainError(error="db error")
    )

    with pytest.raises(DomainError):
        await get_user_details_usecase.execute(
            user_id=1, session_uuid="test-session-uuid"
        )


@pytest.mark.asyncio
async def test_execute_re_raises_domain_error_from_organization_reader(
    get_user_details_usecase,
):
    from src.shared.exceptions.base_exceptions import DomainError

    user = _make_user()
    get_user_details_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=user
    )
    get_user_details_usecase.organization_reader.get_organizations_by_user_id = (
        AsyncMock(side_effect=DomainError(error="db error"))
    )

    with pytest.raises(DomainError):
        await get_user_details_usecase.execute(
            user_id=1, session_uuid="test-session-uuid"
        )


@pytest.mark.asyncio
async def test_execute_wraps_unexpected_error_in_server_error(
    get_user_details_usecase,
):
    from src.shared.exceptions.base_exceptions import ServerError

    get_user_details_usecase.user_domain_service.get_user_by_id = AsyncMock(
        side_effect=ValueError("unexpected")
    )

    with pytest.raises(ServerError):
        await get_user_details_usecase.execute(
            user_id=1, session_uuid="test-session-uuid"
        )
