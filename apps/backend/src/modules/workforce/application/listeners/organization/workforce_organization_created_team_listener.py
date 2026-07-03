from src.modules.organization.domain.events.organization_domain_events import (
    OrganizationCreatedEvent,
)
from src.modules.workforce.application.tasks.default_team_task import (
    seed_default_teams,
)
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.mediator.listener import listener


@listener(OrganizationCreatedEvent)
async def on_organization_created_seed_default_team(event: OrganizationCreatedEvent):
    """
    Inline listener that seeds the default team(s) for a new organization in the
    SAME transaction as the organization creation. Any failure here propagates
    out of mediator.publish(..., raise_on_error=True) and rolls back the entire
    org-creation transaction.
    """
    if event.session is None:
        raise ServerError(
            error="OrganizationCreatedEvent must carry the originating session"
        )

    await seed_default_teams(
        session=event.session,
        organization_id=event.organization_id,
        organization_member_id=event.organization_member_id,
    )


__all__ = ["on_organization_created_seed_default_team"]
