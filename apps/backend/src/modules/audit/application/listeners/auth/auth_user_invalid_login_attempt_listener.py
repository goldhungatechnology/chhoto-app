from src.modules.auth.domain.events.auth_domain_events import (
    UserInvalidLoginAttemptEvent,
)
from src.shared.mediator.listener import listener


@listener(UserInvalidLoginAttemptEvent)
async def audit_on_user_invalid_login_attempt(event: UserInvalidLoginAttemptEvent):
    """
    Audit log for invalid login attempts. This can be used to trigger security measures such as account lockout after a certain number of failed attempts, or to notify the user of suspicious activity on their account.
    """

    from src.shared.infrastructure.audit.audit_writer import write_audit_event
    from src.modules.auth.infrastructure.models.user_model import UserModel

    await write_audit_event(
        action="invalid_login_attempt",
        entity_table=UserModel.__tablename__,
        entity_id=event.user_id,
        before_data={
            "user_id": event.user_id,
            "email": event.email,
            "reason": event.reason,
            "attempt_at": event.attempt_at.isoformat(),
        },
        client_ip=event.ip_address,
        user_agent=(
            event.device + " " + event.browser
            if event.device and event.browser
            else None
        ),
        after_data=None,
    )


__all__ = ["audit_on_user_invalid_login_attempt"]
