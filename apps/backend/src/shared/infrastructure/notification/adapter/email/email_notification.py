from dataclasses import dataclass
from email.message import EmailMessage as SMTPEmailMessage
from pathlib import Path
from typing import Any

from aiosmtplib import SMTP
from jinja2 import Environment, FileSystemLoader

from src.core.config.settings import config
from src.shared.infrastructure.logger import logger

from ...interface.notification_interface import INotification

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
        Render a Jinja2 HTML template and send it as an email.
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
        # Build email message
        # -----------------------------
        msg = SMTPEmailMessage()

        msg["To"] = ", ".join(message.recipient)
        msg["Subject"] = message.subject
        msg["From"] = config.EMAIL_FROM

        msg.set_content("Please view this email in an HTML-compatible email viewer.")

        msg.add_alternative(
            html_body,
            subtype="html",
        )

        # -----------------------------
        # Send email
        # -----------------------------
        smtp = SMTP(
            hostname=config.SMTP_HOST,
            port=config.SMTP_PORT,
            timeout=30,
        )

        try:
            logger.info(
                f"[Email] Connecting to SMTP server "
                f"{config.SMTP_HOST}:{config.SMTP_PORT}"
            )

            await smtp.connect()

            logger.info("[Email] Logging in")

            await smtp.login(
                config.SMTP_USERNAME,
                config.SMTP_PASSWORD,
            )

            logger.info(f"[Email] Sending email to {msg['To']}")

            await smtp.send_message(msg)

            logger.success(
                f"[Email] Email sent successfully to "
                f"{msg['To']} with subject '{msg['Subject']}'"
            )

        except TimeoutError:
            logger.error(f"[Email] Timeout while sending email to {msg['To']}")
            raise

        except Exception as e:
            logger.error(f"[Email] Failed to send email to {msg['To']}: {e!s}")
            raise

        finally:
            try:
                await smtp.quit()
            except Exception:
                pass
