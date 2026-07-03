from dataclasses import dataclass
from src.shared.domain.events.base_domain_events import DomainEvent


@dataclass(kw_only=True, frozen=True)
class UserOnboardingCompletedEvent(DomainEvent):
    """
    Event triggered when a user completes the onboarding process.
    """

    user_id: int
    theme: str
    referral_source: str | None
