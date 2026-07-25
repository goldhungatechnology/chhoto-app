from pathlib import Path

from src.shared.infrastructure.background_task_manager import bgtask
from src.shared.infrastructure.logger import logger
from src.shared.infrastructure.notification import NotificationFactory, InlineImage
from src.shared.infrastructure.notification.adapter.email.email_notification import (
    EmailNotificationMessage,
)

LOGO_PATH = (
    Path(__file__).parent.parent.parent.parent.parent
    / "templates"
    / "auth"
    / "chhoto-logo.png"
)


def _logo_inline_image() -> InlineImage:
    return InlineImage(cid="chhoto-logo", file_path=LOGO_PATH, mime_type="image/png")


async def _send_forgot_password_email(
    *, email: str, link: str, username: str = ""
) -> None:
    """
    Background task to send a forgot password email to the user.
    """
    if not email:
        raise ValueError("email is required for forgot password email task")

    logger.info("[Auth-Email] Attempting to send forgot password email to %s", email)

    try:
        notification = NotificationFactory.create(n_type="email")
        message = EmailNotificationMessage(
            subject="Reset Your Password - Chhoto URL",
            template_name="auth/forgot_password.html",
            context={"link": link, "username": username},
            recipient=[email],
            email_from="noreply@chhoto.tech",
            inline_images=[_logo_inline_image()],
        )
        await notification.send(message)
        logger.success(
            "[Auth-Email] Successfully sent forgot password email to %s", email
        )

    except Exception as e:
        logger.error(
            "[Auth-Email] Failed to send forgot password email to %s. Error: %s. "
            "Will be retried by background worker.",
            email,
            str(e),
        )
        raise


send_forgot_password_email_task = bgtask.add_task(_send_forgot_password_email)
