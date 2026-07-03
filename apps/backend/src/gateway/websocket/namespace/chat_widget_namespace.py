from urllib.parse import parse_qs

from socketio.exceptions import ConnectionRefusedError

from src.gateway.websocket.inteface.websocket_service import IWebSocketService
from src.gateway.websocket.namespace.base_chat_namespace import BaseChatNamespace
from src.modules.visitor.presentation.schemas.visitor_schemas import (
    EndSessionRequestSchema,
)
from src.modules.visitor.visitor_container import get_visitor_container
from src.shared.infrastructure.db import async_session


class ChatWidgetNamespace(BaseChatNamespace):
    """
    Namespace handler for visitor chat widget connections (/widget).
    """

    def __init__(
        self, namespace: str, websocket_service: IWebSocketService | None = None
    ):
        super().__init__(
            namespace=namespace, is_visitor=True, websocket_service=websocket_service
        )

    async def on_connect(self, sid, environ, auth=None):
        auth = auth or {}
        session_uuid = auth.get("session_uuid")

        if not session_uuid:
            query_string = environ.get("QUERY_STRING", "")
            if query_string:
                params = parse_qs(query_string)
                session_uuids = params.get("session_uuid")
                if session_uuids:
                    session_uuid = session_uuids[0]

        if not session_uuid:
            raise ConnectionRefusedError(
                "session_uuid is required for widget connection"
            )

        async with async_session() as db_session:
            container = get_visitor_container(db_session)
            session_service = container.visitor_session_domain_service()
            visitor_session = await session_service.get_session_by_uuid(session_uuid)

        if not visitor_session or visitor_session.is_ended():
            raise ConnectionRefusedError("Invalid or already ended session")

        await self.save_session(sid, {"session_uuid": session_uuid})

    async def on_disconnect(self, sid):
        """
        Disconnect handler: ends the visitor session and page visits in DB/cache.
        """
        try:
            session_data = await self.get_session(sid)
            if not session_data:
                return

            session_uuid = session_data.get("session_uuid")
            if not session_uuid:
                return

            async with async_session() as db_session:
                container = get_visitor_container(db_session)
                usecase = container.end_visitor_session_usecase()
                await usecase.execute(
                    EndSessionRequestSchema(session_uuid=session_uuid)
                )

        except Exception as e:
            print(f"Error in visitor widget disconnect handler: {e}")
