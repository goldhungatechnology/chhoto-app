from src.gateway.websocket.inteface.websocket_service import IWebSocketService
from src.gateway.websocket.socket_manager import sio


class WebSocketService(IWebSocketService):
    """
    Service class wrapping common Socket.IO operations, mirroring the old codebase.
    """

    def __init__(self):
        self.sio = sio

    async def disconnect_agent_ws(self, sid: str) -> None:
        """Placeholder for cleanups on agent websocket disconnect."""
        pass
