from abc import ABC, abstractmethod
from typing import Any


class IOutboxRepository(ABC):
    """
    Interface for the outbox repository.
    """

    @abstractmethod
    async def add(self, event_type: str, payload: dict[str, Any]) -> None:
        """
        Persist an outbox event within the current transaction.
        """
        pass
