from dataclasses import dataclass
from datetime import datetime

from src.shared.domain.events.base_domain_events import DomainEvent


@dataclass(kw_only=True, frozen=True)
class InvitationCreatedEvent(DomainEvent):
    """
    Fired when a new invitation is persisted. The raw token is included so
    listeners (e.g. the email sender) can build the link. It MUST NOT be
    persisted or logged.
    """

    invitation_id: int
    organization_id: int
    email: str
    raw_token: str
    expires_at: datetime


@dataclass(kw_only=True, frozen=True)
class InvitationAcceptedEvent(DomainEvent):
    """
    Fired after an invitation has been accepted and the corresponding
    organization membership has been created.
    """

    invitation_id: int
    organization_id: int
    user_id: int
    organization_member_id: int


@dataclass(kw_only=True, frozen=True)
class InvitationRevokedEvent(DomainEvent):
    """
    Fired when an admin revokes a pending invitation.
    """

    invitation_id: int
    organization_id: int


@dataclass(kw_only=True, frozen=True)
class InvitationResentEvent(DomainEvent):
    """
    Fired when an admin resends an invitation. Carries the new raw token for
    the email sender.
    """

    old_invitation_id: int
    new_invitation_id: int
    organization_id: int
    email: str
    raw_token: str
    expires_at: datetime
