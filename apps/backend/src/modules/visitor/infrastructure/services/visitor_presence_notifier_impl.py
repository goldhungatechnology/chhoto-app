from src.modules.visitor.domain.ports.visitor_presence_notifier import (
    IVisitorPresenceNotifier,
)
from src.gateway.websocket.inteface.realtime_publisher import IRealTimePublisher
from src.gateway.websocket.adapter.socket_publisher import (
    SocketIORealTimePublisher,
)
from src.shared.infrastructure.logger import logger


class VisitorPresenceNotifierImpl(IVisitorPresenceNotifier):
    """
    Pushes visitor presence updates to an organization's connected agents.
    Uses IRealTimePublisher interface to broadcast event payloads.
    """

    def __init__(self, publisher: IRealTimePublisher | None = None):
        self.publisher = publisher or SocketIORealTimePublisher()

    async def notify(self, organization_id: int, message: dict) -> None:
        """
        Best-effort delivery. Emits visitor presence snapshot events
        to agents subscribed to the organization room in Socket.IO.
        """
        try:
            # Emit the event type (e.g. 'visitor.new_session')
            # with the full message payload to the organization's room
            await self.publisher.emit(
                event=message["type"],
                data=message,
                room=f"org_{organization_id}",
                namespace="/agent",
            )
        except Exception as e:  # noqa: BLE001 - presence push is non-critical
            logger.warning(
                "[VisitorPresence] failed to push socket update for org %s: %s",
                organization_id,
                e,
            )
