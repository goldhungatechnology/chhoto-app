from dataclasses import dataclass
from datetime import datetime
from typing import Any
from src.shared.domain.events.base_domain_events import DomainEvent


@dataclass(kw_only=True, frozen=True)
class UserUpdatedEvent(DomainEvent):
    """
    Event triggered when a user is updated.
    """

    user_id: int
    prev_value: Any | None = None
    value: Any | None = None


@dataclass(kw_only=True, frozen=True)
class UserCreatedEvent(DomainEvent):
    """
    Event triggered when a user is created.
    """

    user_id: int
    username: str
    email: str
    token: str


@dataclass(kw_only=True, frozen=True)
class UserInvalidLoginAttemptEvent(DomainEvent):
    """
    Event triggered when a user has an invalid login attempt.
    """

    user_id: int | None = None
    email: str
    reason: str
    attempt_at: datetime
    ip_address: str | None = None
    device: str | None = None
    browser: str | None = None
