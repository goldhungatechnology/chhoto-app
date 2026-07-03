from src.modules.workforce.application.tasks.send_invitation_email_task import (
    send_invitation_email_task,
)
from src.modules.workforce.domain.events.invitation.invitation_domain_events import (
    InvitationCreatedEvent,
    InvitationResentEvent,
)
from src.shared.mediator.listener import listener


def _queue_email(*, email: str, organization_id: int, raw_token: str, expires_at):
    return send_invitation_email_task.queue_with_options(
        task_options={
            "max_retries": 5,
            "min_backoff": 5_000,
            "max_backoff": 300_000,
        },
        email=email,
        organization_id=organization_id,
        raw_token=raw_token,
        expires_at_iso=expires_at.isoformat(),
    )


@listener(InvitationCreatedEvent)
async def on_invitation_created_send_email(event: InvitationCreatedEvent):
    """
    Background email send for newly-issued invitations. Failures retry via
    Dramatiq; they do not roll back the invitation row.
    """
    return _queue_email(
        email=event.email,
        organization_id=event.organization_id,
        raw_token=event.raw_token,
        expires_at=event.expires_at,
    )


@listener(InvitationResentEvent)
async def on_invitation_resent_send_email(event: InvitationResentEvent):
    """
    Background email send for resent invitations.
    """
    return _queue_email(
        email=event.email,
        organization_id=event.organization_id,
        raw_token=event.raw_token,
        expires_at=event.expires_at,
    )


__all__ = [
    "on_invitation_created_send_email",
    "on_invitation_resent_send_email",
]
