from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from src.core.config.settings import config
from src.shared.infrastructure.logger import logger

from ...interface.notification_interface import INotification
from .providers import EmailProviderFactory

TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent.parent.parent / "templates"

_jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=True,
)


@dataclass
class EmailNotificationMessage:
    """
    Email notification message
    """

    subject: str
    template_name: str
    context: dict[str, Any]
    recipient: list[str]


class EmailNotification(INotification[EmailNotificationMessage]):
    """
    Email notification implementation
    """

    async def send(self, message: EmailNotificationMessage):
        """
        Render a Jinja2 HTML template and send it as an email using the configured provider.
        """

        if not message.recipient:
            raise ValueError("Recipient list cannot be empty")

        # -----------------------------
        # Render HTML template
        # -----------------------------
        try:
            template = _jinja_env.get_template(message.template_name)
            html_body = template.render(**message.context)
        except Exception as e:
            logger.error(
                f"[Email] Template render failed: {message.template_name} -> {e!s}"
            )
            raise

        # -----------------------------
        # Get active email provider
        # -----------------------------
        provider_name = config.EMAIL_PROVIDER
        try:
            provider = EmailProviderFactory.get_provider(provider_name)
        except Exception as e:
            logger.error(
                f"[Email] Failed to resolve email provider '{provider_name}': {e!s}"
            )
            raise

        # -----------------------------
        # Send via resolved provider
        # -----------------------------
        await provider.send_email(
            sender=config.EMAIL_FROM,
            recipients=message.recipient,
            subject=message.subject,
            html_body=html_body,
        )
