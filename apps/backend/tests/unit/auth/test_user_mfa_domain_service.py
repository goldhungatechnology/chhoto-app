from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from src.modules.auth.domain.entities.user_mfa_entity import UserMFAEntity
from src.modules.auth.domain.services.user_mfa_domain_service import (
    UserMFADomainService,
)
from src.shared.exceptions.base_exceptions import CreateError


@pytest.mark.asyncio
async def test_create_user_mfa_new_record():
    mock_repo = AsyncMock()
    mock_repo.get_by.return_value = None

    entity_to_add = UserMFAEntity(
        user_id=1,
        secret="NEWSECRET",
        method="TOTP",
        auth_url="otpauth://...",
    )
    mock_repo.add.return_value = entity_to_add

    service = UserMFADomainService(repository=mock_repo)
    result = await service.create_user_mfa(entity_to_add)

    assert result.secret == "NEWSECRET"
    mock_repo.add.assert_called_once_with(entity_to_add)


@pytest.mark.asyncio
async def test_create_user_mfa_update_unverified_record():
    mock_repo = AsyncMock()
    existing_unverified = UserMFAEntity(
        user_id=1,
        secret="OLDSECRET",
        method="TOTP",
        auth_url="old_url",
        verified_at=None,
    )
    mock_repo.get_by.return_value = existing_unverified
    mock_repo.update.side_effect = lambda e: e

    new_entity = UserMFAEntity(
        user_id=1,
        secret="NEWSECRET",
        method="TOTP",
        auth_url="new_url",
    )

    service = UserMFADomainService(repository=mock_repo)
    result = await service.create_user_mfa(new_entity)

    assert result.secret == "NEWSECRET"
    assert result.auth_url == "new_url"
    mock_repo.update.assert_called_once_with(existing_unverified)


@pytest.mark.asyncio
async def test_create_user_mfa_raises_if_already_verified():
    mock_repo = AsyncMock()
    existing_verified = UserMFAEntity(
        user_id=1,
        secret="SECRET",
        method="TOTP",
        auth_url="url",
        verified_at=datetime.now(UTC),
    )
    mock_repo.get_by.return_value = existing_verified

    new_entity = UserMFAEntity(
        user_id=1,
        secret="NEWSECRET",
        method="TOTP",
        auth_url="new_url",
    )

    service = UserMFADomainService(repository=mock_repo)
    with pytest.raises(CreateError) as exc_info:
        await service.create_user_mfa(new_entity)

    assert "MFA is already enabled" in str(exc_info.value)
