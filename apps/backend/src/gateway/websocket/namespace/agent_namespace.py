from src.gateway.events import GatewayEvent
from src.gateway.websocket.inteface.websocket_service import IWebSocketService
from src.gateway.websocket.namespace.base_chat_namespace import BaseChatNamespace
from src.modules.organization.organization_container import get_organization_container
from src.modules.visitor.presentation.schemas.visitor_schemas import (
    AgentSubscriptionPayloadSchema,
)
from src.shared.infrastructure.db import async_session


class AgentNamespace(BaseChatNamespace):
    """
    Namespace handler for agent dashboard connections (/agent).
    """

    def __init__(
        self, namespace: str, websocket_service: IWebSocketService | None = None
    ):
        super().__init__(
            namespace=namespace, is_visitor=False, websocket_service=websocket_service
        )

    async def _emit_error(self, sid: str, message: str) -> None:
        await self.emit(
            GatewayEvent.VISITORS_SUBSCRIBE_ERROR,
            {"error": message},
            room=sid,
        )

    async def _get_organization(self, organization_uuid: str):
        async with async_session() as db_session:
            container = get_organization_container(db_session)
            org_service = container.organization_domain_service()
            return await org_service.get_organization_by_uuid(organization_uuid)

    async def _verify_and_get_member_org(
        self, user_id: int | None, organization_uuid: str
    ):
        """
        Fetches the organization and verifies that the user is an active member.
        Returns the organization instance if valid. Raises ValueError for errors.
        """
        if user_id is None:
            raise ValueError("Authentication required")

        async with async_session() as db_session:
            container = get_organization_container(db_session)
            org_service = container.organization_domain_service()
            member_service = container.organization_member_domain_service()

            organization = await org_service.get_organization_by_uuid(organization_uuid)
            if not organization or organization.id is None:
                raise ValueError("Organization not found")

            is_member = await member_service.is_organization_member(
                organization_id=organization.id,
                user_id=user_id,
            )
            if not is_member:
                raise ValueError("You are not an active member of this organization")

            return organization

    async def on_visitors_subscribe(self, sid, data):
        """
        Event handler triggered when an agent requests to subscribe to an organization's visitor updates.
        Validates the payload, verifies that the agent is an active member of the organization,
        and adds their socket session to the organization's broadcast room.
        """
        session = await self.get_session(sid)
        payload = AgentSubscriptionPayloadSchema.model_validate(data)
        organization_uuid = payload.organization_uuid
        user_id = session.get("user_id") if session else None

        try:
            org = await self._verify_and_get_member_org(user_id, organization_uuid)
        except ValueError as e:
            return await self._emit_error(sid, str(e))

        await self.enter_room(sid, f"org_{org.id}")
        await self.emit(
            GatewayEvent.VISITORS_SUBSCRIBED,
            {"organization_uuid": organization_uuid},
            room=sid,
        )

    async def on_visitors_unsubscribe(self, sid, data):
        """
        Event handler triggered when an agent requests to unsubscribe from an organization's visitor updates.
        Validates the payload and removes their socket session from the organization's broadcast room.
        """
        payload = AgentSubscriptionPayloadSchema.model_validate(data)
        organization_uuid = payload.organization_uuid

        org = await self._get_organization(organization_uuid)
        if org and org.id:
            await self.leave_room(sid, f"org_{org.id}")

        await self.emit(
            GatewayEvent.VISITORS_UNSUBSCRIBED,
            {"organization_uuid": organization_uuid},
            room=sid,
        )
