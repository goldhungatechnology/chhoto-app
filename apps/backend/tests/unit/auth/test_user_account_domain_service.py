from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def user_account_domain_service():
    """
    fixture for user account domain service with mocked repository
    """
    from src.modules.auth.domain.services.user_account_domain_service import (
        UserAccountDomainService,
    )

    mock_repo = AsyncMock()
    mock_repo.add = AsyncMock()

    return UserAccountDomainService(repository=mock_repo)


@pytest.mark.asyncio
async def test_create_user_account_returns_created_entity(user_account_domain_service):
    """
    test that creating a user account returns the created account entity
    """
    from src.modules.auth.domain.entities.user_account_entity import UserAccountEntity

    account_entity = UserAccountEntity(
        type="credentials",
        user_id=1,
        hashed_password="hashed-password",
    )
    created_account = UserAccountEntity(
        id=100,
        type="credentials",
        user_id=1,
        hashed_password="hashed-password",
    )

    user_account_domain_service.repository.add = AsyncMock(return_value=created_account)

    result = await user_account_domain_service.create_user_account(account_entity)

    assert result == created_account
    user_account_domain_service.repository.add.assert_awaited_once_with(account_entity)


@pytest.mark.asyncio
async def test_create_user_account_reraises_domain_error(user_account_domain_service):
    """
    test that domain errors from repository are re-raised unchanged
    """
    from src.modules.auth.domain.entities.user_account_entity import UserAccountEntity
    from src.shared.exceptions.base_exceptions import ConflictError

    account_entity = UserAccountEntity(
        type="credentials",
        user_id=1,
        hashed_password="hashed-password",
    )

    user_account_domain_service.repository.add = AsyncMock(
        side_effect=ConflictError(error="Account already exists")
    )

    with pytest.raises(ConflictError):
        await user_account_domain_service.create_user_account(account_entity)


@pytest.mark.asyncio
async def test_create_user_account_wraps_unexpected_error(user_account_domain_service):
    """
    test that unexpected repository errors are wrapped in CreateError
    """
    from src.modules.auth.domain.entities.user_account_entity import UserAccountEntity
    from src.shared.exceptions.base_exceptions import CreateError

    account_entity = UserAccountEntity(
        type="credentials",
        user_id=1,
        hashed_password="hashed-password",
    )

    user_account_domain_service.repository.add = AsyncMock(
        side_effect=CreateError("db failure")
    )

    with pytest.raises(CreateError):
        await user_account_domain_service.create_user_account(account_entity)
