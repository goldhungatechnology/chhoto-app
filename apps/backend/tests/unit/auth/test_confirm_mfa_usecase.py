from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, UTC
import pytest

from src.modules.auth.application.usecases.mfa.confirm_mfa_usecase import (
    ConfirmMFAUseCase,
)
from src.modules.auth.domain.entities.user_mfa_entity import UserMFAEntity
from src.shared.exceptions.base_exceptions import InvalidError


@pytest.mark.asyncio
async def test_confirm_mfa_success_returns_recovery_codes():
    mock_mfa_domain_service = AsyncMock()
    mock_mfa_recovery_domain_service = AsyncMock()
    mock_totp_service = MagicMock()

    mfa_entity = UserMFAEntity(
        id=10,
        user_id=1,
        secret="SECRET123",
        method="TOTP",
        verified_at=None,
    )
    mock_mfa_domain_service.get_user_mfa_by_user_id.return_value = mfa_entity

    mock_totp_service.verify_totp.return_value = True

    confirmed_entity = UserMFAEntity(
        id=10,
        user_id=1,
        secret="SECRET123",
        method="TOTP",
        verified_at=datetime.now(UTC),
    )
    mock_mfa_domain_service.confirm_user_mfa.return_value = confirmed_entity

    expected_codes = ["9B2A-7K4M", "4P8W-3N1X", "6C9V-2M5T", "1R7Y-8H0Z"]
    mock_mfa_recovery_domain_service.create_recovery_codes_for_mfa.return_value = (
        expected_codes
    )

    usecase = ConfirmMFAUseCase(
        user_mfa_domain_service=mock_mfa_domain_service,
        user_mfa_recovery_domain_service=mock_mfa_recovery_domain_service,
        totp_service=mock_totp_service,
    )

    result = await usecase.execute(user_id=1, otp_code="123456")

    assert result["verified"] is True
    assert result["recovery_codes"] == expected_codes
    mock_mfa_recovery_domain_service.create_recovery_codes_for_mfa.assert_called_once_with(
        mfa_id=10
    )


@pytest.mark.asyncio
async def test_confirm_mfa_invalid_totp_code():
    mock_mfa_domain_service = AsyncMock()
    mock_mfa_recovery_domain_service = AsyncMock()
    mock_totp_service = MagicMock()

    mfa_entity = UserMFAEntity(
        id=10,
        user_id=1,
        secret="SECRET123",
        method="TOTP",
        verified_at=None,
    )
    mock_mfa_domain_service.get_user_mfa_by_user_id.return_value = mfa_entity
    mock_totp_service.verify_totp.return_value = False

    usecase = ConfirmMFAUseCase(
        user_mfa_domain_service=mock_mfa_domain_service,
        user_mfa_recovery_domain_service=mock_mfa_recovery_domain_service,
        totp_service=mock_totp_service,
    )

    with pytest.raises(InvalidError) as exc_info:
        await usecase.execute(user_id=1, otp_code="000000")

    assert "Invalid verification code" in str(exc_info.value)
