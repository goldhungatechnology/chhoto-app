from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def forgot_password_usecase():
    from src.modules.auth.application.usecases.password.forgot_password_usecase import (
        ForgotPasswordUseCase,
    )

    mock_user_domain_service = AsyncMock()
    mock_user_domain_service.get_user_by_email = AsyncMock()

    mock_user_token_domain_service = AsyncMock()
    mock_user_token_domain_service.create_user_token = AsyncMock(
        return_value="raw_token"
    )

    return ForgotPasswordUseCase(
        user_domain_service=mock_user_domain_service,
        user_token_domain_service=mock_user_token_domain_service,
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


@pytest.mark.asyncio
async def test_execute_returns_none_when_user_not_found(forgot_password_usecase):
    forgot_password_usecase.user_domain_service.get_user_by_email = AsyncMock(
        return_value=None
    )

    result = await forgot_password_usecase.execute(email="nonexistent@example.com")

    assert result is None
    forgot_password_usecase.user_token_domain_service.create_user_token.assert_not_called()


@pytest.mark.asyncio
async def test_execute_returns_none_when_user_has_no_id(forgot_password_usecase):
    user = _make_user(id=None)
    forgot_password_usecase.user_domain_service.get_user_by_email = AsyncMock(
        return_value=user
    )

    result = await forgot_password_usecase.execute(email="test@example.com")

    assert result is None
    forgot_password_usecase.user_token_domain_service.create_user_token.assert_not_called()


@pytest.mark.asyncio
async def test_execute_creates_token_with_forgot_password_type(forgot_password_usecase):
    from src.core.config.settings import config

    user = _make_user(id=1, email="test@example.com")
    forgot_password_usecase.user_domain_service.get_user_by_email = AsyncMock(
        return_value=user
    )
    forgot_password_usecase.user_token_domain_service.create_user_token = AsyncMock(
        return_value="raw_token"
    )

    await forgot_password_usecase.execute(email="test@example.com")

    forgot_password_usecase.user_token_domain_service.create_user_token.assert_awaited_once_with(
        user_id=1,
        type="forgot-password",
        expiry_minutes=config.FORGOT_PASSWORD_TOKEN_EXPIRE_MINUTES,
    )


@pytest.mark.asyncio
async def test_execute_publishes_forgot_password_link_created_event(
    forgot_password_usecase,
):
    from src.modules.auth.domain.events.auth_password_domain_events import (
        ForgotPasswordLinkCreatedEvent,
    )
    from src.core.config.settings import config

    user = _make_user(id=1, email="test@example.com")
    forgot_password_usecase.user_domain_service.get_user_by_email = AsyncMock(
        return_value=user
    )
    forgot_password_usecase.user_token_domain_service.create_user_token = AsyncMock(
        return_value="raw_token"
    )

    with patch(
        "src.modules.auth.application.usecases.password.forgot_password_usecase.mediator.publish",
        AsyncMock(),
    ) as mock_publish:
        await forgot_password_usecase.execute(email="test@example.com")

        mock_publish.assert_awaited_once()
        assert mock_publish.await_args is not None
        args, _ = mock_publish.await_args
        (published_event,) = args

        assert isinstance(published_event, ForgotPasswordLinkCreatedEvent)
        assert published_event.email == "test@example.com"
        assert (
            published_event.link
            == f"{config.FRONTEND_URL}/auth/set-password?token=raw_token"
        )


@pytest.mark.asyncio
async def test_execute_re_raises_domain_error(forgot_password_usecase):
    from src.shared.exceptions.base_exceptions import DomainError

    forgot_password_usecase.user_domain_service.get_user_by_email = AsyncMock(
        side_effect=DomainError(error="domain error")
    )

    with pytest.raises(DomainError):
        await forgot_password_usecase.execute(email="test@example.com")


@pytest.mark.asyncio
async def test_execute_wraps_unexpected_error_in_server_error(
    forgot_password_usecase,
):
    from src.shared.exceptions.base_exceptions import ServerError

    forgot_password_usecase.user_domain_service.get_user_by_email = AsyncMock(
        side_effect=ValueError("unexpected")
    )

    with pytest.raises(ServerError):
        await forgot_password_usecase.execute(email="test@example.com")


@pytest.mark.asyncio
async def test_generate_forgot_password_link(forgot_password_usecase):
    from src.core.config.settings import config

    link = await forgot_password_usecase._generate_forgot_password_link("test_token")

    expected = f"{config.FRONTEND_URL}/auth/set-password?token=test_token"
    assert link == expected
