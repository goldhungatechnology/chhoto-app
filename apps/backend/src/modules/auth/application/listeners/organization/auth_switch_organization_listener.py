from src.modules.auth.auth_container import get_auth_container
from src.modules.organization.domain.events.organization_domain_events import (
    OrganizationSwitchedEvent,
)

from src.shared.mediator.listener import listener
from src.shared.mediator.mediator import mediator


@listener(OrganizationSwitchedEvent)
async def on_organization_switched(event: OrganizationSwitchedEvent):
    """
    Listener for handling actions after an organization switch.
    """
    auth_container = get_auth_container(session=event.session)
    session_domain_service = auth_container.user_session_domain_service()
    current_session = await session_domain_service.get_user_session_by_uuid(
        event.current_session_uuid
    )
    if not current_session:
        return

    current_session.organization_uuid = event.target_organization_uuid
    updated_session = await session_domain_service.update_user_session(current_session)

    for e in updated_session.pull_events():
        await mediator.publish(e)
