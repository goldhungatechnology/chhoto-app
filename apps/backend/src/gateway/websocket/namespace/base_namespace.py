from http.cookies import SimpleCookie

import socketio
from socketio.exceptions import ConnectionRefusedError

from src.core.config.settings import config
from src.gateway.websocket.inteface.websocket_service import IWebSocketService
from src.gateway.websocket.services import WebSocketService
from src.modules.auth.auth_container import get_auth_container
from src.modules.auth.infrastructure.cache.auth_cache_service import AuthCacheService
from src.shared.infrastructure.db import async_session
from src.shared.infrastructure.logger import logger


class BaseNamespace(socketio.AsyncNamespace):
    """
    Base Socket.IO namespace class providing shared utilities, logging,
    and default agent dashboard connect/disconnect handlers.
    """

    def __init__(
        self, namespace: str, websocket_service: IWebSocketService | None = None
    ):
        super().__init__(namespace=namespace)
        self.namespace_name = namespace
        self.websocket_service = websocket_service or WebSocketService()

    async def _sid_tracking_key(self, user_id: int) -> str:
        return f"gateway:sids:user:{user_id}"

    async def _disconnect_other_sessions(self, user_id: int, current_sid: str) -> None:
        import redis.asyncio as aioredis
        import typing

        redis: typing.Any = aioredis.from_url(config.REDIS_URL, decode_responses=True)
        key = f"gateway:sids:user:{user_id}"
        old_sids = await redis.smembers(key)
        for old_sid in old_sids:
            if old_sid != current_sid:
                try:
                    if self.server is not None:
                        await self.server.disconnect(old_sid, self.namespace_name)
                except Exception:
                    pass
        await redis.sadd(key, current_sid)
        await redis.expire(key, config.SID_TRACKING_TTL)

    async def _remove_session(self, user_id: int, sid: str) -> None:
        import redis.asyncio as aioredis
        import typing

        redis: typing.Any = aioredis.from_url(config.REDIS_URL, decode_responses=True)
        key = f"gateway:sids:user:{user_id}"
        await redis.srem(key, sid)

    async def on_connect(self, sid, environ, auth):
        """
        Default connect handler for dashboard agents.
        """
        session_uuid = None
        if auth:
            session_uuid = auth.get("session_uuid")

        if not session_uuid:
            cookie_str = environ.get("HTTP_COOKIE", "")
            if cookie_str:
                cookie = SimpleCookie()
                cookie.load(cookie_str)
                if "session_uuid" in cookie:
                    session_uuid = cookie["session_uuid"].value

        if not session_uuid:
            raise ConnectionRefusedError("Unauthorized: session_uuid is required")

        async with async_session() as db_session:
            auth_container = get_auth_container(db_session)
            usecase = auth_container.get_user_session_usecase()
            user_session = await usecase.execute(session_uuid)

        if not user_session:
            raise ConnectionRefusedError("Unauthorized: Session is invalid or expired")

        await self.save_session(sid, {"user_id": user_session.user_id})
        try:
            await self._disconnect_other_sessions(user_session.user_id, sid)
        except Exception:
            logger.warning(
                "Failed to disconnect stale sessions for user %s", user_session.user_id
            )
        await self.enter_room(sid, f"user_{user_session.user_id}")
        await AuthCacheService().set_user_last_seen(user_session.user_id)

    async def on_disconnect(self, sid):
        """
        disconnect handler for agent namespace
        """
        try:
            session = await self.get_session(sid)
            user_id = session.get("user_id") if session else None
            if user_id:
                await self._remove_session(user_id, sid)

            await self.websocket_service.disconnect_agent_ws(sid)
        except Exception as e:
            logger.error(f"Agent Disconnected error: {str(e)}")
