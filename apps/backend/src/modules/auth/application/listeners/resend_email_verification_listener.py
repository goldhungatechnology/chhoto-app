from src.modules.auth.application.tasks.resend_email_verification_task import (
    resend_user_created_email_task,
)
from src.modules.auth.domain.events.auth_email_domain_events import (
    ResendEmailVerificationTokenEvent,
)
from src.shared.mediator.listener import listener


@listener(ResendEmailVerificationTokenEvent)
def on_user_created_resend_email(event: ResendEmailVerificationTokenEvent):
    """
    Queue background email work when a user is created resending email verification.
    """
    return resend_user_created_email_task.queue_with_options(
        task_options={
            "max_retries": 3,
            "min_backoff": 5_000,
            "max_backoff": 60_000,
        },
        email=event.email,
        username=event.username,
        token=event.token,
    )


__all__ = ["on_user_created_resend_email"]
