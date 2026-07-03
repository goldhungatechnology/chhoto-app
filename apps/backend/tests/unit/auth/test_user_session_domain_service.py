from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def user_session_domain_service():
    """
    fixture for user session domain service with mocked repository
    """
    from src.modules.auth.domain.services.user_session_domain_service import (
        UserSessionDomainService,
    )

    mock_repo = AsyncMock()
    mock_repo.add = AsyncMock()

    return UserSessionDomainService(repository=mock_repo)


@pytest.mark.asyncio
async def test_create_user_session_returns_created_entity(user_session_domain_service):
    """
    test that creating a user session returns the created session entity
    """
    from src.modules.auth.domain.entities.user_session_entity import UserSessionEntity

    session_entity = UserSessionEntity(user_id=1, expires_at=datetime.now(UTC))
    created_session = UserSessionEntity(id=200, user_id=1, expires_at=datetime.now(UTC))

    user_session_domain_service.repository.add = AsyncMock(return_value=created_session)

    result = await user_session_domain_service.create_user_session(session_entity)

    assert result == created_session
    user_session_domain_service.repository.add.assert_awaited_once_with(session_entity)


@pytest.mark.asyncio
async def test_create_user_session_wraps_unexpected_error(user_session_domain_service):
    """
    test that unexpected repository errors are wrapped in CreateError
    """
    from src.modules.auth.domain.entities.user_session_entity import UserSessionEntity
    from src.shared.exceptions.base_exceptions import CreateError

    session_entity = UserSessionEntity(user_id=1, expires_at=datetime.now(UTC))

    user_session_domain_service.repository.add = AsyncMock(
        side_effect=CreateError("db failure")
    )

    with pytest.raises(CreateError):
        await user_session_domain_service.create_user_session(session_entity)
