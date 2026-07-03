from dataclasses import dataclass
from datetime import datetime, UTC


@dataclass(frozen=True)
class DomainEvent:
    """
    Base class for domain events.
    """

    occurred_at: datetime = datetime.now(UTC)
