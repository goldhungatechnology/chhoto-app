from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.shared.infrastructure.notification.adapter.email.email_notification import (
    EmailNotification,
    EmailNotificationMessage,
)
from src.shared.infrastructure.notification.adapter.email.providers import (
    EmailProviderFactory,
    ResendProvider,
    SMTPProvider,
    SendGridProvider,
)


def test_provider_factory_returns_correct_providers():
    """
    Test that EmailProviderFactory returns the correct provider instances based on the config name.
    """
    assert isinstance(EmailProviderFactory.get_provider("smtp"), SMTPProvider)
    assert isinstance(EmailProviderFactory.get_provider("resend"), ResendProvider)
    assert isinstance(EmailProviderFactory.get_provider("sendgrid"), SendGridProvider)

    with pytest.raises(ValueError, match="Unsupported email provider"):
        EmailProviderFactory.get_provider("invalid_provider")


@pytest.mark.asyncio
async def test_email_notification_sends_via_resolved_provider():
    """
    Test that EmailNotification renders the template and calls the resolved provider's send_email method.
    """
    mock_provider = AsyncMock()

    with (
        patch(
            "src.shared.infrastructure.notification.adapter.email.email_notification.EmailProviderFactory.get_provider",
            return_value=mock_provider,
        ) as mock_get_provider,
        patch(
            "src.shared.infrastructure.notification.adapter.email.email_notification._jinja_env.get_template"
        ) as mock_get_template,
        patch(
            "src.shared.infrastructure.notification.adapter.email.email_notification.config"
        ) as mock_config,
    ):
        mock_config.EMAIL_PROVIDER = "smtp"
        mock_config.EMAIL_FROM = "sender@example.com"

        mock_template = MagicMock()
        mock_template.render.return_value = "<html>Hello Test</html>"
        mock_get_template.return_value = mock_template

        notification = EmailNotification()
        message = EmailNotificationMessage(
            subject="Test Subject",
            template_name="dummy_template.html",
            context={"name": "Test User"},
            recipient=["recipient@example.com"],
        )

        await notification.send(message)

        # Assert factory is called with correct provider name
        mock_get_provider.assert_called_once_with("smtp")

        # Assert template is fetched and rendered with correct context
        mock_get_template.assert_called_once_with("dummy_template.html")
        mock_template.render.assert_called_once_with(name="Test User")

        # Assert resolved provider's send_email is called with expected parameters
        mock_provider.send_email.assert_awaited_once_with(
            sender="sender@example.com",
            recipients=["recipient@example.com"],
            subject="Test Subject",
            html_body="<html>Hello Test</html>",
        )


@pytest.mark.asyncio
async def test_smtp_provider_calls_smtp_client():
    """
    Test that SMTPProvider creates an SMTP message and sends it via SMTP client.
    """
    mock_smtp_instance = MagicMock()
    mock_smtp_instance.connect = AsyncMock()
    mock_smtp_instance.login = AsyncMock()
    mock_smtp_instance.send_message = AsyncMock()
    mock_smtp_instance.quit = AsyncMock()

    with (
        patch(
            "src.shared.infrastructure.notification.adapter.email.providers.SMTP",
            return_value=mock_smtp_instance,
        ) as mock_smtp_cls,
        patch(
            "src.shared.infrastructure.notification.adapter.email.providers.config"
        ) as mock_config,
    ):
        mock_config.SMTP_HOST = "smtp.mailtrap.io"
        mock_config.SMTP_PORT = 2525
        mock_config.SMTP_USERNAME = "user123"
        mock_config.SMTP_PASSWORD = "pass123"

        provider = SMTPProvider()
        await provider.send_email(
            sender="sender@example.com",
            recipients=["recipient@example.com"],
            subject="Test Subject",
            html_body="<html>Hello Test</html>",
        )

        # Assert SMTP client initialized with config values
        mock_smtp_cls.assert_called_once_with(
            hostname="smtp.mailtrap.io",
            port=2525,
            timeout=30,
        )

        # Assert client flow: connect -> login -> send_message -> quit
        mock_smtp_instance.connect.assert_awaited_once()
        mock_smtp_instance.login.assert_awaited_once_with("user123", "pass123")
        mock_smtp_instance.send_message.assert_awaited_once()
        mock_smtp_instance.quit.assert_awaited_once()


@pytest.mark.asyncio
async def test_resend_provider_calls_resend_sdk():
    """
    Test that ResendProvider sets the API key and calls resend.Emails.send_async.
    """
    with (
        patch(
            "src.shared.infrastructure.notification.adapter.email.providers.config"
        ) as mock_config,
        patch(
            "src.shared.infrastructure.notification.adapter.email.providers.resend"
        ) as mock_resend,
    ):
        mock_send_async = AsyncMock()
        mock_resend.Emails.send_async = mock_send_async
        mock_config.RESEND_API_KEY = "re_test_key_123"

        provider = ResendProvider()
        await provider.send_email(
            sender="Acme <onboarding@resend.dev>",
            recipients=["delivered@resend.dev"],
            subject="hello world",
            html_body="<strong>it works!</strong>",
        )

        # Assert resend API key is configured
        assert mock_resend.api_key == "re_test_key_123"

        # Assert send_async is called with expected parameters
        mock_send_async.assert_awaited_once_with(
            {
                "from": "Acme <onboarding@resend.dev>",
                "to": ["delivered@resend.dev"],
                "subject": "hello world",
                "html": "<strong>it works!</strong>",
            }
        )
