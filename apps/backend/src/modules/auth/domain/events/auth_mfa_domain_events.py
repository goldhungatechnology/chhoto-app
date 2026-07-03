from dataclasses import dataclass

from src.shared.domain.events.base_domain_events import DomainEvent


@dataclass(kw_only=True, frozen=True)
class MFASetupCompletedEvent(DomainEvent):
    """
    Event triggered when an MFA setup is completed (confirmed).
    """

    user_id: int


@dataclass(kw_only=True, frozen=True)
class MFADisabledEvent(DomainEvent):
    """
    Event triggered when an MFA is disabled for a user.
    """

    user_id: int
