from abc import ABC, abstractmethod


class IVisitorPresenceNotifier(ABC):
    """
    Port for pushing real-time visitor presence updates to the agents of an
    organization (implemented over the WebSocket gateway backplane).
    """

    @abstractmethod
    async def notify(self, organization_id: int, message: dict) -> None:
        """
        Deliver ``message`` to every connected agent subscribed to this
        organization's visitor presence channel. Best-effort: delivery failures
        must not break the originating request.
        """
