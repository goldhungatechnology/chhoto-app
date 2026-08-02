from unittest.mock import AsyncMock, MagicMock
from datetime import UTC, datetime

import pytest

from src.modules.auth.application.usecases.mfa.verify_mfa_usecase import (
    VerifyMFAUseCase,
)
from src.modules.auth.domain.entities.user_mfa_entity import UserMFAEntity
from src.modules.auth.domain.entities.user_session_entity import UserSessionEntity
from src.shared.exceptions.base_exceptions import InvalidError


def _build_usecase(**overrides) -> VerifyMFAUseCase:
    mock_mfa_domain_service = AsyncMock()
    mock_recovery_domain_service = AsyncMock()
    mock_session_domain_service = AsyncMock()
    mock_totp_service = MagicMock()
    mock_token_service = MagicMock()

    mock_token_service.validate_token.return_value = {
        "user_id": 1,
        "type": "mfa",
    }
    mock_mfa_domain_service.get_verified_user_mfa_by_user_id.return_value = (
        UserMFAEntity(
            id=10,
            user_id=1,
            secret="SECRET123",
            method="TOTP",
            verified_at=datetime.now(UTC),
        )
    )
    mock_session_domain_service.list_sessions_by_user_id.return_value = []
    created_session = UserSessionEntity(
        id=5,
        uuid="session-uuid-123",
        user_id=1,
        expires_at=datetime.now(UTC),
    )
    mock_session_domain_service.create_user_session.return_value = created_session

    defaults = {
        "user_mfa_domain_service": mock_mfa_domain_service,
        "user_mfa_recovery_domain_service": mock_recovery_domain_service,
        "user_session_domain_service": mock_session_domain_service,
        "totp_service": mock_totp_service,
        "token_service": mock_token_service,
    }
    defaults.update(overrides)
    return VerifyMFAUseCase(**defaults)


@pytest.mark.asyncio
async def test_verify_mfa_success_with_otp_code():
    usecase = _build_usecase()
    usecase.totp_service.verify_totp.return_value = True

    result = await usecase.execute(
        temp_token="temp-token",
        otp_code="123456",
        ip_address="127.0.0.1",
        device="test-device",
        browser="test-browser",
    )

    assert result["session_uuid"] == "session-uuid-123"
    usecase.totp_service.verify_totp.assert_called_once_with("SECRET123", "123456")
    usecase.user_mfa_recovery_domain_service.verify_recovery_code.assert_not_called()


@pytest.mark.asyncio
async def test_verify_mfa_invalid_otp_code():
    usecase = _build_usecase()
    usecase.totp_service.verify_totp.return_value = False

    with pytest.raises(InvalidError) as exc_info:
        await usecase.execute(
            temp_token="temp-token",
            otp_code="000000",
        )

    assert "Invalid MFA code" in str(exc_info.value)
    usecase.user_session_domain_service.create_user_session.assert_not_called()


@pytest.mark.asyncio
async def test_verify_mfa_success_with_recovery_code():
    usecase = _build_usecase()
    usecase.user_mfa_recovery_domain_service.verify_recovery_code.return_value = True

    result = await usecase.execute(
        temp_token="temp-token",
        recovery_code="9B2A-7K4M",
        ip_address="127.0.0.1",
        device="test-device",
        browser="test-browser",
    )

    assert result["session_uuid"] == "session-uuid-123"
    usecase.user_mfa_recovery_domain_service.verify_recovery_code.assert_called_once_with(
        mfa_id=10, plain_code="9B2A-7K4M"
    )
    usecase.totp_service.verify_totp.assert_not_called()


@pytest.mark.asyncio
async def test_verify_mfa_invalid_recovery_code():
    usecase = _build_usecase()
    usecase.user_mfa_recovery_domain_service.verify_recovery_code.return_value = False

    with pytest.raises(InvalidError) as exc_info:
        await usecase.execute(
            temp_token="temp-token",
            recovery_code="0000-0000",
        )

    assert "Invalid recovery code" in str(exc_info.value)
    usecase.user_session_domain_service.create_user_session.assert_not_called()


@pytest.mark.asyncio
async def test_verify_mfa_missing_credentials():
    usecase = _build_usecase()

    with pytest.raises(InvalidError) as exc_info:
        await usecase.execute(
            temp_token="temp-token",
        )

    assert "TOTP code or a recovery code" in str(exc_info.value)
    usecase.user_session_domain_service.create_user_session.assert_not_called()


@pytest.mark.asyncio
async def test_verify_mfa_invalid_temp_token_type():
    usecase = _build_usecase()
    usecase.token_service.validate_token.return_value = {
        "user_id": 1,
        "type": "access",
    }

    with pytest.raises(InvalidError) as exc_info:
        await usecase.execute(
            temp_token="temp-token",
            otp_code="123456",
        )

    assert "Invalid token type" in str(exc_info.value)
    usecase.user_mfa_domain_service.get_verified_user_mfa_by_user_id.assert_not_called()
