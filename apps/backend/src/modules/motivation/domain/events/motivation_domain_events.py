from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.events.base_domain_events import DomainEvent


@dataclass(kw_only=True, frozen=True)
class DailyMotivationConfigCreatedEvent(DomainEvent):
    """
    Event triggered when daily motivation config is created for an organization.
    """

    actor_id: int
    organization_id: int
    config_id: int
    session: AsyncSession | None = None


@dataclass(kw_only=True, frozen=True)
class DailyMotivationConfigUpdatedEvent(DomainEvent):
    """
    Event triggered when daily motivation config is updated.
    """

    actor_id: int
    organization_id: int
    config_id: int
    session: AsyncSession | None = None


@dataclass(kw_only=True, frozen=True)
class DailyMotivationConfigResetEvent(DomainEvent):
    """
    Event triggered when daily motivation config is reset to default.
    """

    actor_id: int
    organization_id: int
    config_id: int
    session: AsyncSession | None = None


@dataclass(kw_only=True, frozen=True)
class CustomMotivationQuoteCreatedEvent(DomainEvent):
    """
    Event triggered when a custom motivation quote is created.
    """

    actor_id: int
    organization_id: int
    quote_uuid: str
    session: AsyncSession | None = None


@dataclass(kw_only=True, frozen=True)
class CustomMotivationQuoteUpdatedEvent(DomainEvent):
    """
    Event triggered when a custom motivation quote is updated.
    """

    actor_id: int
    organization_id: int
    quote_uuid: str
    session: AsyncSession | None = None


@dataclass(kw_only=True, frozen=True)
class CustomMotivationQuoteDeletedEvent(DomainEvent):
    """
    Event triggered when a custom motivation quote is deleted.
    """

    actor_id: int
    organization_id: int
    quote_uuid: str
    session: AsyncSession | None = None


@dataclass(kw_only=True, frozen=True)
class CustomMotivationQuoteStatusChangedEvent(DomainEvent):
    """
    Event triggered when a custom motivation quote status is changed.
    """

    actor_id: int
    organization_id: int
    quote_uuid: str
    old_status: str
    new_status: str
    session: AsyncSession | None = None


@dataclass(kw_only=True, frozen=True)
class MotivationQuoteReactionAddedOrUpdatedEvent(DomainEvent):
    """
    Event triggered when a member adds or updates reaction on a motivation quote.
    """

    actor_id: int
    organization_id: int
    member_id: int
    quote_uuid: str
    reaction_id: int
    reaction_type: str
    session: AsyncSession | None = None
