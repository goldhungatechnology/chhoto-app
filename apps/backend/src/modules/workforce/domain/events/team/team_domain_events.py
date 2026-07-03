from dataclasses import dataclass

from src.shared.domain.events.base_domain_events import DomainEvent


@dataclass(kw_only=True, frozen=True)
class TeamCreatedEvent(DomainEvent):
    """
    Event triggered when a team is created.
    """

    team_id: int
    organization_id: int
    name: str


@dataclass(kw_only=True, frozen=True)
class TeamUpdatedEvent(DomainEvent):
    """
    Event triggered when a team is updated.
    """

    team_id: int
    organization_id: int


@dataclass(kw_only=True, frozen=True)
class TeamDeletedEvent(DomainEvent):
    """
    Event triggered when a team is deleted.
    """

    team_id: int
    organization_id: int


@dataclass(kw_only=True, frozen=True)
class TeamMemberAddedEvent(DomainEvent):
    """
    Event triggered when a member is added to a team.
    """

    team_member_id: int
    organization_id: int
    team_id: int
    member_id: int
    role: str


@dataclass(kw_only=True, frozen=True)
class TeamMemberRemovedEvent(DomainEvent):
    """
    Event triggered when a member is removed from a team.
    """

    team_member_id: int
    organization_id: int
    team_id: int
    member_id: int
    role: str


@dataclass(kw_only=True, frozen=True)
class TeamMemberRoleAssignedEvent(DomainEvent):
    """
    Event triggered when a team member's role is changed.
    """

    team_member_id: int
    organization_id: int
    team_id: int
    member_id: int
    role: str
