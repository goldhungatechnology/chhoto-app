from src.modules.motivation.application.tasks.seed_default_quotes_task import (
    seed_default_quotes_for_organization,
)
from src.modules.organization.domain.events.organization_domain_events import (
    OrganizationCreatedEvent,
)
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.mediator.listener import listener


@listener(OrganizationCreatedEvent)
async def on_organization_created_seed_motivation_quotes(
    event: OrganizationCreatedEvent,
):
    """
    Inline listener that seeds default motivation quotes for the organization
    in the SAME transaction as the organization creation.
    """
    if event.session is None:
        raise ServerError(
            error="OrganizationCreatedEvent must carry the originating session"
        )

    await seed_default_quotes_for_organization(
        session=event.session,
        organization_id=event.organization_id,
        actor_id=event.actor_id,
    )


__all__ = ["on_organization_created_seed_motivation_quotes"]
