from dataclasses import dataclass
from src.shared.domain.events.base_domain_events import DomainEvent


@dataclass(kw_only=True, frozen=True)
class ResendEmailVerificationTokenEvent(DomainEvent):
    """
    Event triggered when a user requests to resend the email verification token.
    """

    username: str
    email: str
    token: str
