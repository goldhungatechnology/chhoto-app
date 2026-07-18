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


async def _resend_user_created_email(*, email: str, username: str, token: str) -> None:
    """
    ReSends the welcome/verification email for newly created users.
    Raise on failure so Dramatiq retries the task.
    Logs retry attempt information for monitoring.
    """
    if not email:
        raise ValueError("email is required for resend  email task")

    logger.info("[Auth-Email] Attempting to resend user-created email to %s", email)

    try:
        notification = NotificationFactory.create(n_type="email")
        message = EmailNotificationMessage(
            subject="Verify Your Email - Chhoto URL",
            template_name="auth/email_verification.html",
            context={"username": username, "token": token},
            recipient=[email],
            email_from="noreply@chhoto.tech",
            inline_images=[_logo_inline_image()],
        )
        await notification.send(message)
        logger.success(
            "[Auth-Email] Successfully re-sent user-created email to %s", email
        )

    except Exception as e:
        logger.error(
            "[Auth-Email] Failed to resend user-created email to %s. Error: %s. "
            "Will be retried by background worker.",
            email,
            str(e),
        )
        raise


resend_user_created_email_task = bgtask.add_task(_resend_user_created_email)
