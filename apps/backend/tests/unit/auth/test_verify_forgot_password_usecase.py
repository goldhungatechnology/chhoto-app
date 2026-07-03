from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def verify_forgot_password_usecase():
    from src.modules.auth.application.usecases.password.verify_forgot_password_usecase import (
        VerifyForgotPasswordUseCase,
    )

    mock_user_domain_service = AsyncMock()
    mock_user_domain_service.get_user_by_id = AsyncMock()

    mock_user_account_domain_service = AsyncMock()
    mock_user_account_domain_service.get_user_account_by_user_id = AsyncMock()
    mock_user_account_domain_service.update_user_account = AsyncMock()

    mock_user_token_domain_service = AsyncMock()
    mock_user_token_domain_service.get_user_token_by_token = AsyncMock()

    mock_hasher = MagicMock()
    mock_hasher.verify = MagicMock(return_value=True)
    mock_hasher.hash = MagicMock(return_value="new_hashed_password")

    mock_revoke_all_user_sessions_usecase = AsyncMock()
    mock_revoke_all_user_sessions_usecase.execute = AsyncMock(return_value=0)

    return VerifyForgotPasswordUseCase(
        user_domain_service=mock_user_domain_service,
        user_account_domain_service=mock_user_account_domain_service,
        user_token_domain_service=mock_user_token_domain_service,
        revoke_all_user_sessions_usecase=mock_revoke_all_user_sessions_usecase,
        hasher=mock_hasher,
    )


def _make_user(**overrides):
    from src.modules.auth.domain.entities.user_entity import UserEntity

    data = {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "avatar_bg": "#ffffff",
        "status": "active",
    }
    data.update(overrides)
    return UserEntity(**data)


def _make_token(**overrides):
    from src.modules.auth.domain.entities.user_token_entity import UserTokenEntity

    data = {
        "user_id": 1,
        "type": "forgot-password",
        "token_hash": "hashed_token",
        "expires_at": datetime.now(UTC) + timedelta(hours=1),
    }
    data.update(overrides)
    return UserTokenEntity(**data)


def _make_account(**overrides):
    from src.modules.auth.domain.entities.user_account_entity import (
        UserAccountEntity,
    )

    data = {
        "id": 1,
        "type": "credentials",
        "user_id": 1,
        "hashed_password": "old_hashed_password",
    }
    data.update(overrides)
    return UserAccountEntity(**data)


@pytest.mark.asyncio
async def test_execute_changes_password_successfully(
    verify_forgot_password_usecase,
):
    token_entity = _make_token()
    user = _make_user()
    account = _make_account()

    verify_forgot_password_usecase.user_token_domain_service.get_user_token_by_token = (
        AsyncMock(return_value=token_entity)
    )
    verify_forgot_password_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=user
    )
    verify_forgot_password_usecase.user_account_domain_service.get_user_account_by_user_id = AsyncMock(
        return_value=account
    )

    await verify_forgot_password_usecase.execute(
        token="valid_token",
        new_password="new_pass",
    )

    verify_forgot_password_usecase.user_token_domain_service.get_user_token_by_token.assert_awaited_once_with(
        token="valid_token", type="forgot-password"
    )
    verify_forgot_password_usecase.user_domain_service.get_user_by_id.assert_awaited_once_with(
        user_id=1
    )
    verify_forgot_password_usecase.user_account_domain_service.get_user_account_by_user_id.assert_awaited_once_with(
        user_id=1, type="credentials"
    )
    # The emailed token is the sole proof of identity; the old password must
    # NOT be requested or verified during a forgot-password reset.
    verify_forgot_password_usecase.hasher.verify.assert_not_called()
    verify_forgot_password_usecase.hasher.hash.assert_called_once_with("new_pass")
    assert account.hashed_password == "new_hashed_password"
    verify_forgot_password_usecase.user_account_domain_service.update_user_account.assert_awaited_once_with(
        account
    )
    # The reset token must be consumed so the link is single-use.
    verify_forgot_password_usecase.user_token_domain_service.mark_token_as_used.assert_awaited_once_with(
        token_entity
    )
    # All existing sessions must be revoked on a successful reset.
    verify_forgot_password_usecase.revoke_all_user_sessions_usecase.execute.assert_awaited_once_with(
        user_id=1
    )


@pytest.mark.asyncio
async def test_execute_raises_invalid_error_when_token_not_found(
    verify_forgot_password_usecase,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    verify_forgot_password_usecase.user_token_domain_service.get_user_token_by_token = (
        AsyncMock(return_value=None)
    )

    with pytest.raises(InvalidError, match="Invalid or expired token"):
        await verify_forgot_password_usecase.execute(
            token="invalid_token",
            new_password="new_pass",
        )


@pytest.mark.asyncio
async def test_execute_raises_invalid_error_when_token_has_no_user_id(
    verify_forgot_password_usecase,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    token_entity = _make_token(user_id=None)
    verify_forgot_password_usecase.user_token_domain_service.get_user_token_by_token = (
        AsyncMock(return_value=token_entity)
    )

    with pytest.raises(InvalidError, match="Invalid or expired token"):
        await verify_forgot_password_usecase.execute(
            token="token",
            new_password="new_pass",
        )


@pytest.mark.asyncio
async def test_execute_raises_invalid_error_when_user_not_found(
    verify_forgot_password_usecase,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    token_entity = _make_token(user_id=1)
    verify_forgot_password_usecase.user_token_domain_service.get_user_token_by_token = (
        AsyncMock(return_value=token_entity)
    )
    verify_forgot_password_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=None
    )

    with pytest.raises(InvalidError, match="Invalid or expired token"):
        await verify_forgot_password_usecase.execute(
            token="token",
            new_password="new_pass",
        )

    verify_forgot_password_usecase.user_account_domain_service.get_user_account_by_user_id.assert_not_called()


@pytest.mark.asyncio
async def test_execute_raises_invalid_error_when_account_not_found(
    verify_forgot_password_usecase,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    token_entity = _make_token()
    user = _make_user()

    verify_forgot_password_usecase.user_token_domain_service.get_user_token_by_token = (
        AsyncMock(return_value=token_entity)
    )
    verify_forgot_password_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=user
    )
    verify_forgot_password_usecase.user_account_domain_service.get_user_account_by_user_id = AsyncMock(
        return_value=None
    )

    with pytest.raises(InvalidError, match="User account not found"):
        await verify_forgot_password_usecase.execute(
            token="token",
            new_password="new_pass",
        )


@pytest.mark.asyncio
async def test_execute_raises_invalid_error_when_account_no_hashed_password(
    verify_forgot_password_usecase,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    token_entity = _make_token()
    user = _make_user()
    account = _make_account(hashed_password=None)

    verify_forgot_password_usecase.user_token_domain_service.get_user_token_by_token = (
        AsyncMock(return_value=token_entity)
    )
    verify_forgot_password_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=user
    )
    verify_forgot_password_usecase.user_account_domain_service.get_user_account_by_user_id = AsyncMock(
        return_value=account
    )

    with pytest.raises(InvalidError, match="You have to first setup your password"):
        await verify_forgot_password_usecase.execute(
            token="token",
            new_password="new_pass",
        )


@pytest.mark.asyncio
async def test_execute_raises_invalid_error_when_account_not_credentials(
    verify_forgot_password_usecase,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    token_entity = _make_token()
    user = _make_user()
    account = _make_account(type="oauth", hashed_password="some_hash")

    verify_forgot_password_usecase.user_token_domain_service.get_user_token_by_token = (
        AsyncMock(return_value=token_entity)
    )
    verify_forgot_password_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=user
    )
    verify_forgot_password_usecase.user_account_domain_service.get_user_account_by_user_id = AsyncMock(
        return_value=account
    )

    with pytest.raises(InvalidError, match="You have to first setup your password"):
        await verify_forgot_password_usecase.execute(
            token="token",
            new_password="new_pass",
        )


@pytest.mark.asyncio
async def test_execute_re_raises_domain_error_from_user_lookup(
    verify_forgot_password_usecase,
):
    from src.shared.exceptions.base_exceptions import DomainError

    verify_forgot_password_usecase.user_token_domain_service.get_user_token_by_token = (
        AsyncMock(side_effect=DomainError(error="db error"))
    )

    with pytest.raises(DomainError):
        await verify_forgot_password_usecase.execute(
            token="token",
            new_password="new_pass",
        )


@pytest.mark.asyncio
async def test_execute_wraps_unexpected_error_in_server_error(
    verify_forgot_password_usecase,
):
    from src.shared.exceptions.base_exceptions import ServerError

    verify_forgot_password_usecase.user_token_domain_service.get_user_token_by_token = (
        AsyncMock(side_effect=ValueError("unexpected"))
    )

    with pytest.raises(ServerError):
        await verify_forgot_password_usecase.execute(
            token="token",
            new_password="new_pass",
        )


@pytest.mark.asyncio
async def test_execute_re_raises_domain_error_from_password_change(
    verify_forgot_password_usecase,
):
    from src.shared.exceptions.base_exceptions import DomainError

    token_entity = _make_token()
    user = _make_user()

    verify_forgot_password_usecase.user_token_domain_service.get_user_token_by_token = (
        AsyncMock(return_value=token_entity)
    )
    verify_forgot_password_usecase.user_domain_service.get_user_by_id = AsyncMock(
        return_value=user
    )
    verify_forgot_password_usecase.user_account_domain_service.get_user_account_by_user_id = AsyncMock(
        side_effect=DomainError(error="domain error")
    )

    with pytest.raises(DomainError):
        await verify_forgot_password_usecase.execute(
            token="token",
            new_password="new_pass",
        )
