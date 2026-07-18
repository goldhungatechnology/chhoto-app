from pathlib import Path

from src.shared.infrastructure.logger import logger
from src.shared.infrastructure.notification import NotificationFactory, InlineImage
from src.shared.infrastructure.notification.adapter.email.email_notification import (
    EmailNotificationMessage,
)
from src.shared.infrastructure.outbox.outbox_registry import outbox_handler
from src.shared.integrations.events.event_types import EventType

LOGO_PATH = (
    Path(__file__).parent.parent.parent.parent.parent
    / "templates"
    / "auth"
    / "chhoto-logo.png"
)


def _logo_inline_image() -> InlineImage:
    return InlineImage(cid="chhoto-logo", file_path=LOGO_PATH, mime_type="image/png")


@outbox_handler(EventType.USER_CREATED)
async def handle_user_created_email_notification(payload: dict) -> None:
    """
    Handle user-created outbox event by sending an email notification.
    """
    email = payload.get("email")
    username = payload.get("username")
    token = payload.get("token")

    if not isinstance(email, str) or not email:
        raise ValueError("USER_CREATED payload must include a valid 'email'")

    logger.info(f"[Outbox] Sending user-created notification email to {email}")
    notification = NotificationFactory.create(n_type="email")
    message = EmailNotificationMessage(
        subject="Verify Your Email - Chhoto URL",
        template_name="auth/email_verification.html",
        context={"username": username, "token": token or ""},
        recipient=[email],
        email_from="noreply@chhoto.tech",
        inline_images=[_logo_inline_image()],
    )

    await notification.send(message)
    logger.info(f"[Outbox] Send user-created notification email to {email}")
