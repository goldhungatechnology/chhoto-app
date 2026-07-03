import uuid
from datetime import UTC, datetime
from dataclasses import dataclass, field, asdict, is_dataclass

from src.shared.domain.events.base_domain_events import DomainEvent


@dataclass
class BaseEntity:
    """
    base entity for every domain entity
    """

    id: int | None = None
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None
    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def mark_updated(self):
        """
        mark the entity as updated
        """

        self.updated_at = datetime.now(UTC)

    def add_event(self, event: DomainEvent):
        """
        add a domain event to the entity
        """

        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        """
        pull the domain events from the entity and clear the events list
        """

        events = self._events[:]
        self._events.clear()
        return events

    def to_cache_dict(self) -> dict:
        """
        Returns a safe dictionary representation for cache storage.

        Rules:
        - removes _events (runtime-only state)
        - converts datetime → ISO string
        - does NOT include methods or behavior
        """

        if is_dataclass(self):
            data = asdict(self)
        else:
            data = dict(self.__dict__)

        # Always remove runtime/internal state
        data.pop("_events", None)

        # Normalize datetime fields
        for key, value in list(data.items()):
            if isinstance(value, datetime):
                data[key] = value.isoformat()

        return data
