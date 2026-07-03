from abc import ABC, abstractmethod


class IRealTimePublisher(ABC):
    """
    Port defining how the backend services publish real-time events.
    """

    @abstractmethod
    async def emit(
        self, event: str, data: dict, room: str, namespace: str = "/"
    ) -> None:
        """
        Emit an event to a specific room in a namespace.
        """
        pass
