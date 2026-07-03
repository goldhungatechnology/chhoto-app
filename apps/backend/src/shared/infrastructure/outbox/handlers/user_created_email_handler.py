from src.shared.infrastructure.logger import logger
from src.shared.infrastructure.notification import NotificationFactory
from src.shared.infrastructure.notification.adapter.email.email_notification import (
    EmailNotificationMessage,
)
from src.shared.infrastructure.outbox.outbox_registry import outbox_handler
from src.shared.integrations.events.event_types import EventType


@outbox_handler(EventType.USER_CREATED)
async def handle_user_created_email_notification(payload: dict) -> None:
    """
    Handle user-created outbox event by sending an email notification.
    """
    email = payload.get("email")
    username = payload.get("username")

    if not isinstance(email, str) or not email:
        raise ValueError("USER_CREATED payload must include a valid 'email'")

    logger.info(f"[Outbox] Sending user-created notification email to {email}")
    notification = NotificationFactory.create(n_type="email")
    message = EmailNotificationMessage(
        subject="Welcome to Our Service!",
        template_name="auth/email_verification.html",
        context={"username": username},
        recipient=[email],
    )

    await notification.send(message)
    logger.info(f"[Outbox] Send user-created notification email to {email}")
