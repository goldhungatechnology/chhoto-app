from dataclasses import dataclass

from src.shared.domain.events.base_domain_events import DomainEvent


@dataclass(kw_only=True, frozen=True)
class ForgotPasswordLinkCreatedEvent(DomainEvent):
    """
    Event triggered when a forgot password reset link is created.
    """

    email: str
    link: str


@dataclass(kw_only=True, frozen=True)
class PasswordChangedEvent(DomainEvent):
    """
    Event triggered when a user's password is successfully changed.
    """

    user_id: int
