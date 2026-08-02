from unittest.mock import AsyncMock, MagicMock

import pytest

from src.modules.auth.domain.entities.user_mfa_recovery_entity import (
    UserMFARecoveryCodeEntity,
)
from src.modules.auth.domain.services.user_mfa_recovery_domain_service import (
    UserMFARecoveryDomainService,
)


def _build_service():
    repository = AsyncMock()
    hasher_service = MagicMock()
    service = UserMFARecoveryDomainService(
        repository=repository, hasher_service=hasher_service
    )
    return service, repository, hasher_service


def _code(cid: int, hashed: str) -> UserMFARecoveryCodeEntity:
    return UserMFARecoveryCodeEntity(
        id=cid,
        mfa_id=10,
        hashed_recovery_code=hashed,
    )


@pytest.mark.asyncio
async def test_verify_recovery_code_success_revokes_code():
    service, repository, hasher_service = _build_service()
    active_codes = [
        _code(1, "hash-9B2A-7K4M"),
        _code(2, "hash-4P8W-3N1X"),
    ]
    repository.get_by_mfa_id.return_value = active_codes

    def fake_verify(hashed: str, plain: str) -> bool:
        return hashed == f"hash-{plain}"

    hasher_service.verify.side_effect = fake_verify

    result = await service.verify_recovery_code(mfa_id=10, plain_code="9B2A-7K4M")

    assert result is True
    assert active_codes[0].is_revoked is True
    assert active_codes[1].is_revoked is False
    repository.update.assert_called_once_with(active_codes[0])


@pytest.mark.asyncio
async def test_verify_recovery_code_normalizes_input():
    service, repository, hasher_service = _build_service()
    active_codes = [_code(1, "hash-9B2A-7K4M")]
    repository.get_by_mfa_id.return_value = active_codes

    def fake_verify(hashed: str, plain: str) -> bool:
        return hashed == f"hash-{plain}"

    hasher_service.verify.side_effect = fake_verify

    result = await service.verify_recovery_code(mfa_id=10, plain_code="  9b2a-7k4m  ")

    assert result is True
    # The stripped, uppercased code is what gets verified.
    assert "9B2A-7K4M" in hasher_service.verify.call_args[0][1]


@pytest.mark.asyncio
async def test_verify_recovery_code_no_match_returns_false():
    service, repository, hasher_service = _build_service()
    active_codes = [_code(1, "hash-9B2A-7K4M")]
    repository.get_by_mfa_id.return_value = active_codes

    def fake_verify(hashed: str, plain: str) -> bool:
        return hashed == f"hash-{plain}"

    hasher_service.verify.side_effect = fake_verify

    result = await service.verify_recovery_code(mfa_id=10, plain_code="0000-0000")

    assert result is False
    assert active_codes[0].is_revoked is False
    repository.update.assert_not_called()
