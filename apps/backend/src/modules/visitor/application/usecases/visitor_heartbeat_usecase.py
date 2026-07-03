from datetime import UTC, datetime

from src.modules.visitor.domain.constants import EVENT_HEARTBEAT, PRESENCE_TTL_SECONDS
from src.modules.visitor.domain.ports.visitor_presence_notifier import (
    IVisitorPresenceNotifier,
)
from src.modules.visitor.domain.ports.visitor_presence_store import (
    IVisitorPresenceStore,
)
from src.modules.visitor.domain.services.visitor_domain_service import (
    VisitorDomainService,
)
from src.modules.visitor.domain.services.visitor_session_domain_service import (
    VisitorSessionDomainService,
)
from src.modules.visitor.domain.value_objects.visitor_presence import (
    VisitorPresence,
    parse_user_agent,
)
from src.modules.visitor.presentation.schemas.visitor_schemas import (
    HeartbeatRequestSchema,
)
from src.shared.exceptions.base_exceptions import (
    DomainError,
    InvalidError,
    ServerError,
)


class VisitorHeartbeatUseCase:
    """
    Keeps a visitor's presence alive. The fast path is pure Redis (refresh TTL +
    last-seen). If the presence has expired between beats it is transparently
    rebuilt from the still-active session in the database.
    """

    def __init__(
        self,
        presence_store: IVisitorPresenceStore,
        visitor_session_domain_service: VisitorSessionDomainService,
        visitor_domain_service: VisitorDomainService,
        presence_notifier: IVisitorPresenceNotifier,
    ):
        self.presence_store = presence_store
        self.visitor_session_domain_service = visitor_session_domain_service
        self.visitor_domain_service = visitor_domain_service
        self.presence_notifier = presence_notifier

    async def execute(self, payload: HeartbeatRequestSchema) -> dict:
        """Execute the heartbeat flow."""
        try:
            now_iso = datetime.now(UTC).isoformat()
            session_uuid = payload.session_uuid

            index = await self.presence_store.get_session_index(session_uuid)
            if index is not None:
                organization_id, visitor_id = index
                refreshed = await self.presence_store.touch(
                    organization_id=organization_id,
                    visitor_id=visitor_id,
                    last_seen=now_iso,
                    ttl=PRESENCE_TTL_SECONDS,
                )
                await self.presence_store.set_session_index(
                    session_uuid=session_uuid,
                    organization_id=organization_id,
                    visitor_id=visitor_id,
                    ttl=PRESENCE_TTL_SECONDS,
                )
                if refreshed:
                    await self.presence_notifier.notify(
                        organization_id,
                        {
                            "type": EVENT_HEARTBEAT,
                            "session_uuid": session_uuid,
                            "visitor_id": visitor_id,
                            "last_seen": now_iso,
                        },
                    )
                    return {"status": "active"}

            # Slow path: presence expired (or index missing) — rebuild from DB.
            return await self._rebuild_from_db(session_uuid, now_iso)
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to process heartbeat", internal_details=str(e)
            ) from e

    async def _rebuild_from_db(self, session_uuid: str, now_iso: str) -> dict:
        session = await self.visitor_session_domain_service.get_session_by_uuid(
            session_uuid
        )
        if not session or session.is_ended():
            raise InvalidError(error="Session not found or already ended")

        visitor = await self.visitor_domain_service.get_by_id(session.visitor_id)

        # Calculate active duration from past ended sessions
        active_duration = 0
        try:
            past_sessions = await self.visitor_session_domain_service.repository.filter(
                visitor_id=session.visitor_id
            )
            for s in past_sessions:
                if s.is_ended() and s.ended_at:
                    active_duration += int((s.ended_at - s.started_at).total_seconds())
        except Exception:
            pass

        device, browser = parse_user_agent(session.user_agent)

        presence = VisitorPresence(
            organization_id=session.organization_id,
            visitor_id=session.visitor_id,
            visitor_uuid=visitor.uuid if visitor else session.uuid,
            session_uuid=session.uuid,
            status="active",
            last_seen=now_iso,
            page=session.landing_page,
            name=visitor.name if visitor else None,
            email=visitor.email if visitor else None,
            phone=visitor.phone if visitor else None,
            external_id=visitor.external_id if visitor else None,
            visit_count=visitor.visit_count if visitor else 1,
            is_identified=visitor.is_identified if visitor else False,
            device=device,
            browser=browser,
            ip_address=session.ip_address,
            active_duration=active_duration,
        )
        await self.presence_store.set_presence(presence, PRESENCE_TTL_SECONDS)
        await self.presence_store.set_session_index(
            session_uuid=session.uuid,
            organization_id=session.organization_id,
            visitor_id=session.visitor_id,
            ttl=PRESENCE_TTL_SECONDS,
        )
        await self.presence_notifier.notify(
            session.organization_id,
            {"type": EVENT_HEARTBEAT, "visitor": presence.to_dict()},
        )
        return {"status": "active"}
