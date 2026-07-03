import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC

from fastapi import WebSocket


@dataclass
class Connection:
    """
    Represents a WebSocket connection for a user. It encapsulates the WebSocket instance, connection type, unique connection ID, and the timestamp when the connection was established. The Connection class provides methods for sending JSON messages to the client and closing the connection gracefully. It also includes an internal lock to ensure that messages are sent sequentially without race
    """

    websocket: WebSocket
    type: str
    connection_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    connected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _send_lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)

    async def send_json(self, data: dict) -> None:
        """
        Send a JSON message to the client. This method uses an internal lock to ensure that messages are sent sequentially, preventing
        """
        async with self._send_lock:
            await self.websocket.send_json(data)

    async def close(self, code: int = 1000) -> None:
        """
        Close the WebSocket connection gracefully. The method attempts to close the connection using the provided code and ignores any exceptions that may occur during the closing process. This ensures that the connection is closed without raising errors, even if the connection is already closed or if there are issues with the WebSocket instance.
        """
        try:
            await self.websocket.close(code=code)
        except Exception:
            pass
