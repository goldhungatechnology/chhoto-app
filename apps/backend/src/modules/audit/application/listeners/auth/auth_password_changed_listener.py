from src.modules.auth.domain.events.auth_password_domain_events import (
    PasswordChangedEvent,
)
from src.shared.mediator.listener import listener


@listener(PasswordChangedEvent)
async def audit_on_password_changed(event: PasswordChangedEvent):
    """
    Audit log for password changes.
    """
    from src.modules.auth.infrastructure.models.user_account_model import (
        UserAccountModel,
    )
    from src.shared.infrastructure.audit.audit_writer import write_audit_event

    await write_audit_event(
        action="password_changed",
        entity_table=UserAccountModel.__tablename__,
        entity_id=event.user_id,
        before_data=None,
        after_data=None,
    )


__all__ = ["audit_on_password_changed"]
