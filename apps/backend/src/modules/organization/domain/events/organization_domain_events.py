from dataclasses import dataclass
from src.shared.domain.events.base_domain_events import DomainEvent
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(kw_only=True, frozen=True)
class OrganizationCreatedEvent(DomainEvent):
    """
    Event triggered when an organization is created.
    """

    actor_id: int
    organization_id: int
    organization_member_id: int
    session: AsyncSession | None = None


@dataclass(kw_only=True, frozen=True)
class OrganizationSwitchedEvent(DomainEvent):
    """
    Event triggered when an organization is switched.
    """

    actor_id: int
    target_organization_uuid: str
    current_session_uuid: str
    session: AsyncSession


@dataclass(kw_only=True, frozen=True)
class OrganizationUpdatedEvent(DomainEvent):
    """
    Event triggered when an organization is updated.
    """

    actor_id: int
    organization_id: int
    session: AsyncSession | None = None


@dataclass(kw_only=True, frozen=True)
class OrganizationActivatedEvent(DomainEvent):
    """
    Event triggered after an organization completes provisioning and its status
    is flipped to active. Listeners on this event run as background follow-ups
    (welcome email, analytics, billing customer, etc.) and must NOT be relied
    on for must-succeed setup.
    """

    actor_id: int
    organization_id: int
    organization_member_id: int
