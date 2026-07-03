from datetime import UTC, datetime

from src.modules.visitor.domain.constants import (
    EVENT_PAGE_CHANGED,
    PRESENCE_TTL_SECONDS,
)
from src.modules.visitor.domain.ports.visitor_presence_notifier import (
    IVisitorPresenceNotifier,
)
from src.modules.visitor.domain.ports.visitor_presence_store import (
    IVisitorPresenceStore,
)
from src.modules.visitor.domain.services.visitor_domain_service import (
    VisitorDomainService,
)
from src.modules.visitor.domain.services.visitor_page_visit_domain_service import (
    VisitorPageVisitDomainService,
)
from src.modules.visitor.domain.services.visitor_session_domain_service import (
    VisitorSessionDomainService,
)
from src.modules.visitor.domain.value_objects.visitor_presence import (
    VisitorPresence,
    parse_user_agent,
)
from src.modules.visitor.presentation.schemas.visitor_schemas import (
    PageEnterRequestSchema,
)
from src.shared.exceptions.base_exceptions import (
    DomainError,
    InvalidError,
    ServerError,
)


class TrackPageEnterUseCase:
    """
    Records a page change for an active session: closes the previous open page
    visit, opens a new one, and refreshes the live presence snapshot.
    """

    def __init__(
        self,
        visitor_session_domain_service: VisitorSessionDomainService,
        visitor_page_visit_domain_service: VisitorPageVisitDomainService,
        visitor_domain_service: VisitorDomainService,
        presence_store: IVisitorPresenceStore,
        presence_notifier: IVisitorPresenceNotifier,
    ):
        self.visitor_session_domain_service = visitor_session_domain_service
        self.visitor_page_visit_domain_service = visitor_page_visit_domain_service
        self.visitor_domain_service = visitor_domain_service
        self.presence_store = presence_store
        self.presence_notifier = presence_notifier

    async def execute(self, payload: PageEnterRequestSchema) -> dict:
        """Execute the page-enter flow."""
        try:
            session = await self.visitor_session_domain_service.get_session_by_uuid(
                payload.session_uuid
            )
            if not session or session.id is None or session.is_ended():
                raise InvalidError(error="Session not found or already ended")

            organization_id = session.organization_id
            visitor_id = session.visitor_id

            await self.visitor_page_visit_domain_service.enter_page(
                organization_id=organization_id,
                session_id=session.id,
                visitor_id=visitor_id,
                url=payload.url,
                page_title=payload.page_title,
            )

            visitor = await self.visitor_domain_service.get_by_id(visitor_id)

            device, browser = parse_user_agent(session.user_agent)

            presence = VisitorPresence(
                organization_id=organization_id,
                visitor_id=visitor_id,
                visitor_uuid=visitor.uuid if visitor else session.uuid,
                session_uuid=session.uuid,
                status="active",
                last_seen=datetime.now(UTC).isoformat(),
                page=payload.url,
                name=visitor.name if visitor else None,
                email=visitor.email if visitor else None,
                phone=visitor.phone if visitor else None,
                external_id=visitor.external_id if visitor else None,
                visit_count=visitor.visit_count if visitor else 1,
                is_identified=visitor.is_identified if visitor else False,
                device=device,
                browser=browser,
                ip_address=session.ip_address,
                active_duration=0,
            )
            await self.presence_store.set_presence(presence, PRESENCE_TTL_SECONDS)
            await self.presence_store.set_session_index(
                session_uuid=session.uuid,
                organization_id=organization_id,
                visitor_id=visitor_id,
                ttl=PRESENCE_TTL_SECONDS,
            )

            await self.presence_notifier.notify(
                organization_id,
                {"type": EVENT_PAGE_CHANGED, "visitor": presence.to_dict()},
            )

            return {"session_uuid": session.uuid, "url": payload.url}
        except DomainError:
            raise
        except Exception as error:
            raise ServerError(
                error="Failed to track page visit", internal_details=str(error)
            ) from error
