"""
WebSocket event handlers that let an authenticated agent opt in/out of an
organization's live visitor presence feed.

After connecting to ``/ws/connect`` an agent sends:

    {"type": "visitors.subscribe", "payload": {"organization_uuid": "<uuid>"}}

We verify the agent is an active member of that organization before joining the
org's presence room. Once subscribed, every visitor presence update for that org
(pushed via ``connection_manager.publish_to_org``) is delivered to the agent.
"""

from src.gateway.events import GatewayEvent
from src.gateway.ws.connection_manager import connection_manager
from src.gateway.ws.routers.event_router import global_event_router
from src.modules.organization.infrastructure.repositories.organization_member_repository_impl import (
    OrganizationMemberRepositoryImpl,
)
from src.modules.organization.infrastructure.services.organization_reader_impl import (
    get_organization_reader,
)
from src.shared.infrastructure.db import async_session


async def _resolve_member_org_id(user_id: int, organization_uuid: str) -> int | None:
    """
    Resolve an organization uuid to its internal id, but only if ``user_id`` is
    an active member. Returns ``None`` when the org is unknown or the user is not
    an active member.
    """
    async with async_session() as session:
        organization = await get_organization_reader(session).get_organization_by_uuid(
            organization_uuid
        )
        if not organization or organization.id is None:
            return None

        member_repository = OrganizationMemberRepositoryImpl(session=session)
        member = await member_repository.get_by(
            organization_id=organization.id, user_id=user_id, status="active"
        )
        return organization.id if member else None


@global_event_router.register(GatewayEvent.VISITORS_SUBSCRIBE)
async def handle_visitors_subscribe(user_id: int, payload: dict) -> dict:
    """Subscribe the agent to an organization's visitor presence feed."""
    organization_uuid = payload.get("organization_uuid")
    if not organization_uuid:
        return {
            "type": GatewayEvent.VISITORS_SUBSCRIBE_ERROR,
            "error": "organization_uuid is required",
        }

    organization_id = await _resolve_member_org_id(user_id, organization_uuid)
    if organization_id is None:
        return {
            "type": GatewayEvent.VISITORS_SUBSCRIBE_ERROR,
            "error": "Organization not found or you are not a member",
        }

    connection_manager.subscribe_to_org(organization_id, user_id)
    return {
        "type": GatewayEvent.VISITORS_SUBSCRIBED,
        "organization_uuid": organization_uuid,
    }


@global_event_router.register(GatewayEvent.VISITORS_UNSUBSCRIBE)
async def handle_visitors_unsubscribe(user_id: int, payload: dict) -> dict:
    """Unsubscribe the agent from an organization's visitor presence feed."""
    organization_uuid = payload.get("organization_uuid")
    if not organization_uuid:
        return {
            "type": GatewayEvent.VISITORS_UNSUBSCRIBE_ERROR,
            "error": "organization_uuid is required",
        }

    organization_id = await _resolve_member_org_id(user_id, organization_uuid)
    if organization_id is not None:
        connection_manager.unsubscribe_from_org(organization_id, user_id)
    return {
        "type": GatewayEvent.VISITORS_UNSUBSCRIBED,
        "organization_uuid": organization_uuid,
    }
