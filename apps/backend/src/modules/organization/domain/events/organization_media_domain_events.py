from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.events.base_domain_events import DomainEvent


@dataclass(kw_only=True, frozen=True)
class OrganizationMediaCreatedEvent(DomainEvent):
    """
    Event triggered when organization media is created.
    """

    actor_id: int
    organization_id: int
    organization_media_id: int
    session: AsyncSession | None = None


@dataclass(kw_only=True, frozen=True)
class OrganizationMediaUpdatedEvent(DomainEvent):
    """
    Event triggered when organization media is updated.
    """

    actor_id: int
    organization_id: int
    organization_media_id: int
    session: AsyncSession | None = None
