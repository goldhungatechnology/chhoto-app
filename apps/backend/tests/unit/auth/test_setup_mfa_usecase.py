from unittest.mock import AsyncMock, MagicMock

import pytest

from src.modules.auth.application.usecases.mfa.setup_mfa_usecase import SetupMFAUseCase
from src.modules.auth.domain.entities.user_mfa_entity import UserMFAEntity
from src.shared.exceptions.base_exceptions import DomainError


@pytest.mark.asyncio
async def test_setup_mfa_success_new():
    mock_user_domain_service = AsyncMock()
    mock_user_mfa_domain_service = AsyncMock()
    mock_totp_service = MagicMock()

    user = MagicMock()
    user.id = 1
    user.email = "test@example.com"
    mock_user_domain_service.get_user_by_id.return_value = user

    mock_totp_service.generate_secret.return_value = "SECRET123"
    mock_totp_service.generate_auth_url.return_value = "otpauth://totp/..."

    created_entity = UserMFAEntity(
        user_id=1,
        secret="SECRET123",
        method="TOTP",
        auth_url="otpauth://totp/...",
    )
    mock_user_mfa_domain_service.create_user_mfa.return_value = created_entity

    usecase = SetupMFAUseCase(
        user_domain_service=mock_user_domain_service,
        user_mfa_domain_service=mock_user_mfa_domain_service,
        totp_service=mock_totp_service,
    )

    res = await usecase.execute(user_id=1)

    assert res["secret"] == "SECRET123"
    assert res["auth_url"] == "otpauth://totp/..."
    mock_user_mfa_domain_service.create_user_mfa.assert_called_once()


@pytest.mark.asyncio
async def test_setup_mfa_user_not_found():
    mock_user_domain_service = AsyncMock()
    mock_user_mfa_domain_service = AsyncMock()
    mock_totp_service = MagicMock()

    mock_user_domain_service.get_user_by_id.return_value = None

    usecase = SetupMFAUseCase(
        user_domain_service=mock_user_domain_service,
        user_mfa_domain_service=mock_user_mfa_domain_service,
        totp_service=mock_totp_service,
    )

    with pytest.raises(DomainError):
        await usecase.execute(user_id=999)
