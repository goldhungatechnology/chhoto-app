from dataclasses import dataclass
from src.shared.domain.events.base_domain_events import DomainEvent


@dataclass(kw_only=True, frozen=True)
class RoleCreatedEvent(DomainEvent):
    """
    Event triggered when a role is created.
    """

    role_id: int
    organization_id: int
    name: str


@dataclass(kw_only=True, frozen=True)
class MemberRoleCreatedEvent(DomainEvent):
    """
    Event triggered when a member role is created.
    """

    member_role_id: int
    member_id: int
    role_id: int


@dataclass(kw_only=True, frozen=True)
class DefaultRolesAssignedEvent(DomainEvent):
    """
    Event triggered when default roles are assigned to a new organization.
    """

    organization_id: int
