from datetime import datetime

from src.core.config.settings import config
from src.modules.organization.infrastructure.services.organization_reader_impl import (
    get_organization_reader,
)
from src.shared.infrastructure.background_task_manager import bgtask
from src.shared.infrastructure.db import async_session
from src.shared.infrastructure.logger import logger
from src.shared.infrastructure.notification import NotificationFactory
from src.shared.infrastructure.notification.adapter.email.email_notification import (
    EmailNotificationMessage,
)


async def _send_invitation_email(
    *,
    email: str,
    organization_id: int,
    raw_token: str,
    expires_at_iso: str,
) -> None:
    """
    Sends the invitation email. Opens its own session to resolve the
    organization name (since the originating transaction has already
    committed by the time this task runs). Raises on failure so Dramatiq
    retries with exponential backoff.
    """
    if not email:
        raise ValueError("email is required for invitation email task")
    if not raw_token:
        raise ValueError("raw_token is required for invitation email task")

    organization_name = "your organization"
    try:
        async with async_session() as session:
            org_reader = get_organization_reader(session)
            org = await org_reader.get_organization(organization_id)
            if org:
                organization_name = org.name
    except Exception as e:
        logger.warning(
            "[Workforce-Invitation] Could not resolve org name for id=%s: %s",
            organization_id,
            str(e),
        )

    invite_link = f"{config.FRONTEND_URL}/invite/{raw_token}"
    try:
        expires_at_display = datetime.fromisoformat(expires_at_iso).strftime(
            "%Y-%m-%d %H:%M UTC"
        )
    except ValueError:
        expires_at_display = expires_at_iso

    logger.info("[Workforce-Invitation] Sending invitation email to %s", email)

    try:
        notification = NotificationFactory.create(n_type="email")
        message = EmailNotificationMessage(
            subject=f"You've been invited to {organization_name}",
            template_name="workforce/invitation.html",
            context={
                "organization_name": organization_name,
                "invite_link": invite_link,
                "expires_at": expires_at_display,
            },
            recipient=[email],
        )
        await notification.send(message)
        logger.success("[Workforce-Invitation] Sent invitation email to %s", email)
    except Exception as e:
        logger.error(
            "[Workforce-Invitation] Failed to send invitation email to %s: %s",
            email,
            str(e),
        )
        raise


send_invitation_email_task = bgtask.add_task(_send_invitation_email)
