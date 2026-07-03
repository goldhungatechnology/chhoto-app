import traceback

import socketio
from socketio import AsyncRedisManager

from src.core.config.settings import config
from src.shared.infrastructure.logger import logger

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    reconnection=True,
)


def configure_socket_server(server: socketio.AsyncServer) -> None:
    """
    Configure the Redis client manager and register default events.
    """
    redis_manager = AsyncRedisManager(
        config.REDIS_URL,
        channel="socketio",
    )
    setattr(server, "client_manager", redis_manager)
    redis_manager.set_server(server)

    @sio.event
    async def connect(sid, environ, auth):
        logger.info(
            "Socket connected: sid=%s, ip=%s, auth=%s",
            sid,
            environ.get("REMOTE_ADDR"),
            auth,
        )
        return True


def register_namespaces(server: socketio.AsyncServer) -> None:
    """Register application-specific namespaces."""
    from src.gateway.websocket.namespace.agent_namespace import AgentNamespace
    from src.gateway.websocket.namespace.chat_widget_namespace import (
        ChatWidgetNamespace,
    )

    server.register_namespace(AgentNamespace("/agent"))
    server.register_namespace(ChatWidgetNamespace("/widget"))


def create_socket_app():
    from src.main import create_app

    app = create_app()

    try:
        configure_socket_server(sio)
        register_namespaces(sio)

        return socketio.ASGIApp(
            socketio_server=sio,
            other_asgi_app=app,
            socketio_path="/ws/socket/socket.io",
        )

    except Exception:
        logger.exception("Failed to initialize Socket.IO server")
        traceback.print_exc()
        return app
