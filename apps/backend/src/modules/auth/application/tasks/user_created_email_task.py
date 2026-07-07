from src.shared.infrastructure.background_task_manager import bgtask
from src.shared.infrastructure.logger import logger
from src.shared.infrastructure.notification import NotificationFactory
from src.shared.infrastructure.notification.adapter.email.email_notification import (
    EmailNotificationMessage,
)


async def _send_user_created_email(*, email: str, username: str, token: str) -> None:
    """
    Sends the welcome/verification email for newly created users.
    Raise on failure so Dramatiq retries the task.
    Logs retry attempt information for monitoring.
    """
    if not email:
        raise ValueError("email is required for user-created email task")

    logger.info("[Auth-Email] Attempting to send user-created email to %s", email)

    try:
        notification = NotificationFactory.create(n_type="email")
        message = EmailNotificationMessage(
            subject="Welcome to Our Service!",
            template_name="auth/email_verification.html",
            context={"username": username, "token": token},
            recipient=[email],
            email_from="noreply@chhoto.tech",
        )
        await notification.send(message)
        logger.success("[Auth-Email] Successfully sent user-created email to %s", email)

    except Exception as e:
        logger.error(
            "[Auth-Email] Failed to send user-created email to %s. Error: %s. "
            "Will be retried by background worker.",
            email,
            str(e),
        )
        raise


send_user_created_email_task = bgtask.add_task(_send_user_created_email)
