from src.modules.auth.application.tasks.user_created_email_task import (
    send_user_created_email_task,
)
from src.modules.auth.domain.events.auth_domain_events import UserCreatedEvent
from src.shared.mediator.listener import listener


@listener(UserCreatedEvent)
def on_user_created(event: UserCreatedEvent):
    """
    Queue background email work when a user is created.
    """
    return send_user_created_email_task.queue_with_options(
        task_options={
            "max_retries": 3,
            "min_backoff": 5_000,
            "max_backoff": 60_000,
        },
        email=event.email,
        username=event.username,
        token=event.token,
    )


__all__ = ["on_user_created"]
