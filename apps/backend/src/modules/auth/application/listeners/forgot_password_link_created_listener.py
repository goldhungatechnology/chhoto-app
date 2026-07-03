from src.modules.auth.application.tasks.forgot_password_email_task import (
    send_forgot_password_email_task,
)
from src.modules.auth.domain.events.auth_password_domain_events import (
    ForgotPasswordLinkCreatedEvent,
)
from src.shared.mediator.listener import listener


@listener(ForgotPasswordLinkCreatedEvent)
def on_forgot_password_link_created(event: ForgotPasswordLinkCreatedEvent):
    """
    Queue background email work when a user is created.
    """
    return send_forgot_password_email_task.queue_with_options(
        task_options={
            "max_retries": 3,
            "min_backoff": 5_000,
            "max_backoff": 60_000,
        },
        email=event.email,
        link=event.link,
    )


__all__ = ["on_forgot_password_link_created"]
