from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def user_token_domain_service():
    """
    fixture for user token domain service with mocked dependencies
    """
    from src.modules.auth.domain.services.user_token_domain_service import (
        UserTokenDomainService,
    )

    mock_repo = AsyncMock()
    mock_repo.add = AsyncMock()
    mock_repo.get_by = AsyncMock()
    mock_repo.update = AsyncMock()

    mock_token_service = MagicMock()
    mock_token_service.random_token = MagicMock(return_value="abc123")

    mock_hasher = MagicMock()
    mock_hasher.deterministic_hash = MagicMock(return_value="hashed_abc123")

    return UserTokenDomainService(
        repository=mock_repo,
        token_service=mock_token_service,
        hasher=mock_hasher,
    )


@pytest.mark.asyncio
async def test_create_user_token_returns_raw_token(user_token_domain_service):
    """
    test that creating a user token returns the raw (unhashed) token string
    """
    result = await user_token_domain_service.create_user_token(
        user_id=1, type="email_verification"
    )

    assert result == "abc123"


@pytest.mark.asyncio
async def test_create_user_token_stores_hashed_token(user_token_domain_service):
    """
    test that create_user_token stores the hashed version of the token in the repository
    """
    from src.modules.auth.domain.entities.user_token_entity import UserTokenEntity

    await user_token_domain_service.create_user_token(
        user_id=1, type="email_verification"
    )

    user_token_domain_service.repository.add.assert_awaited_once()
    args, _ = user_token_domain_service.repository.add.await_args
    (created_entity,) = args

    assert isinstance(created_entity, UserTokenEntity)
    assert created_entity.user_id == 1
    assert created_entity.type == "email_verification"
    assert created_entity.token_hash == "hashed_abc123"
    assert created_entity.used_at is None


@pytest.mark.asyncio
async def test_create_user_token_sets_expiry_from_default(user_token_domain_service):
    """
    test that create_user_token sets the expires_at to now + default expiry (24 hours)
    """
    from datetime import timedelta

    now = datetime.now(UTC)

    await user_token_domain_service.create_user_token(
        user_id=1, type="email_verification"
    )

    user_token_domain_service.repository.add.assert_awaited_once()
    args, _ = user_token_domain_service.repository.add.await_args
    (created_entity,) = args

    expected_min = now + timedelta(hours=24) - timedelta(seconds=1)
    expected_max = now + timedelta(hours=24) + timedelta(seconds=1)
    assert expected_min <= created_entity.expires_at <= expected_max


@pytest.mark.asyncio
async def test_create_user_token_with_custom_expiry(user_token_domain_service):
    """
    test that create_user_token accepts a custom expiry_minutes override
    """
    now = datetime.now(UTC)

    await user_token_domain_service.create_user_token(
        user_id=1, type="email_verification", expiry_minutes=30
    )

    user_token_domain_service.repository.add.assert_awaited_once()
    args, _ = user_token_domain_service.repository.add.await_args
    (created_entity,) = args

    expected_min = now + timedelta(minutes=30) - timedelta(seconds=1)
    expected_max = now + timedelta(minutes=30) + timedelta(seconds=1)
    assert expected_min <= created_entity.expires_at <= expected_max


@pytest.mark.asyncio
async def test_create_user_token_calls_add_with_audit_false(user_token_domain_service):
    """
    test that create_user_token passes audit=False to repository.add
    """
    await user_token_domain_service.create_user_token(
        user_id=1, type="email_verification"
    )

    user_token_domain_service.repository.add.assert_awaited_once()
    _, kwargs = user_token_domain_service.repository.add.await_args
    assert kwargs.get("audit") is False


@pytest.mark.asyncio
async def test_create_user_token_generates_token_with_config_digit(
    user_token_domain_service,
):
    """
    test that the token_service.random_token is called with the configured digit length
    """
    from src.core.config.settings import config

    await user_token_domain_service.create_user_token(
        user_id=1, type="email_verification"
    )

    user_token_domain_service.token_service.random_token.assert_called_once_with(
        digit=config.TOKEN_DIGIT
    )


@pytest.mark.asyncio
async def test_verify_user_token_returns_true_and_entity_when_found(
    user_token_domain_service,
):
    """
    test that verify_user_token returns (True, entity) when a valid token is found
    """
    from src.modules.auth.domain.entities.user_token_entity import UserTokenEntity

    expected_entity = UserTokenEntity(
        user_id=1,
        type="email_verification",
        token_hash="hashed_abc123",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    user_token_domain_service.repository.get_by = AsyncMock(
        return_value=expected_entity
    )

    valid, entity = await user_token_domain_service.verify_user_token(
        type="email_verification", user_id=1, token="abc123"
    )

    assert valid is True
    assert entity is expected_entity


@pytest.mark.asyncio
async def test_verify_user_token_returns_false_and_none_when_not_found(
    user_token_domain_service,
):
    """
    test that verify_user_token returns (False, None) when no matching token exists
    """
    user_token_domain_service.repository.get_by = AsyncMock(return_value=None)

    valid, entity = await user_token_domain_service.verify_user_token(
        type="email_verification", user_id=1, token="invalid_token"
    )

    assert valid is False
    assert entity is None


@pytest.mark.asyncio
async def test_verify_user_token_queries_with_correct_filters(
    user_token_domain_service,
):
    """
    test that verify_user_token queries the repository with the right filters including hash
    """
    user_token_domain_service.repository.get_by = AsyncMock(return_value=None)

    await user_token_domain_service.verify_user_token(
        type="email_verification", user_id=1, token="abc123"
    )

    user_token_domain_service.repository.get_by.assert_awaited_once()
    call_args = user_token_domain_service.repository.get_by.await_args
    assert call_args is not None
    _args, kwargs = call_args
    assert kwargs["type"] == "email_verification"
    assert kwargs["user_id"] == 1
    assert isinstance(kwargs["expires_at__gt"], datetime)
    assert kwargs["used_at"] is None
    assert kwargs["token_hash"] == "hashed_abc123"


@pytest.mark.asyncio
async def test_verify_user_token_hashes_provided_token(user_token_domain_service):
    """
    test that verify_user_token hashes the provided token before querying
    """
    user_token_domain_service.repository.get_by = AsyncMock(return_value=None)

    await user_token_domain_service.verify_user_token(
        type="email_verification", user_id=1, token="raw_token_value"
    )

    user_token_domain_service.hasher.deterministic_hash.assert_called_once_with(
        "raw_token_value"
    )


@pytest.mark.asyncio
async def test_mark_token_as_used_calls_repository_update(user_token_domain_service):
    """
    test that mark_token_as_used calls repository.update with the token
    """
    from src.modules.auth.domain.entities.user_token_entity import UserTokenEntity

    token_entity = UserTokenEntity(
        user_id=1,
        type="email_verification",
        token_hash="hashed_abc123",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )

    await user_token_domain_service.mark_token_as_used(token_entity)

    user_token_domain_service.repository.update.assert_awaited_once_with(
        token_entity, audit=False
    )
