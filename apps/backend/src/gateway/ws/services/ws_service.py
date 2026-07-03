from fastapi import WebSocket

from src.modules.auth.infrastructure.cache.auth_cache_service import AuthCacheService
from src.shared.exceptions.base_exceptions import UnAuthorizedError
from src.shared.infrastructure.db import async_session
from src.shared.infrastructure.middlewares.policy.policy_registry import (
    get_session_reader,
)


class WebsocketService:
    """
    A service class responsible for handling WebSocket connections, including authentication and connection type determination. The service uses the AuthCacheService to manage user session data and ensure that only authenticated users can establish WebSocket connections. It retrieves the session UUID from the WebSocket cookies, validates the session against the database, and updates the user's last seen timestamp in the cache. The service also provides a method to determine the type of connection based on query parameters.
    """

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self._cache_service = AuthCacheService()

    def get_connection_type(self) -> str:
        """
        Determine the type of WebSocket connection based on query parameters. The connection type is specified by the "type" query parameter in the WebSocket URL. If the "type" parameter is not provided, it defaults to "chat". This allows the gateway to support different types of WebSocket connections (e.g., chat, notifications, etc.) and route them accordingly.
        """
        return self.websocket.query_params.get("type", "chat")

    async def authenticate(self) -> int:
        """
        Authenticate the WebSocket connection by validating the session UUID from the cookies. The method retrieves the session UUID from the WebSocket cookies, checks if it exists, and then queries the database to validate the session. If the session is valid and not expired or revoked, it updates the user's last seen timestamp in the cache and returns the user ID associated with the session. If the session is invalid or expired, an UnAuthorizedError is raised.
        """
        session_uuid = self.websocket.cookies.get("session_uuid")
        if not session_uuid:
            raise UnAuthorizedError(
                errors={"code": "UNAUTHENTICATED"},
                error="session_uuid cookie is required",
            )

        async with async_session() as db_session:
            session_reader = get_session_reader(db_session)
            user_session = await session_reader.get_user_session(session_uuid)

        if not user_session or user_session.is_expired() or user_session.is_revoked():
            raise UnAuthorizedError(
                errors={"code": "SESSION_EXPIRED"},
                error="Session expired or invalid",
            )

        await self._cache_service.set_user_last_seen(user_session.user_id)
        return user_session.user_id
