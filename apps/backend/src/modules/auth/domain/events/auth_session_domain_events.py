from dataclasses import dataclass
from typing import Any
from src.shared.domain.events.base_domain_events import DomainEvent


@dataclass(kw_only=True, frozen=True)
class UserSessionUpdatedEvent(DomainEvent):
    """
    Event triggered when a user session is updated
    """

    session_uuid: str
    prev_value: Any | None = None
    value: Any | None = None
