from src.gateway.websocket.inteface.websocket_service import IWebSocketService
from src.gateway.websocket.namespace.base_namespace import BaseNamespace


class BaseChatNamespace(BaseNamespace):
    """
    Base namespace for handling chat-related websocket interactions.
    Inherited by both AgentNamespace and ChatWidgetNamespace.
    """

    def __init__(
        self,
        namespace: str,
        is_visitor: bool = False,
        websocket_service: IWebSocketService | None = None,
    ):
        super().__init__(namespace=namespace, websocket_service=websocket_service)
        self.is_visitor = is_visitor
