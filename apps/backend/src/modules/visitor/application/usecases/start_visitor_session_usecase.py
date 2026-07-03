from datetime import UTC, datetime

from src.modules.organization.domain.ports.organization.organization_reader import (
    OrganizationReader,
)
from src.modules.visitor.domain.constants import (
    EVENT_SESSION_STARTED,
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
    StartSessionRequestSchema,
)
from src.shared.exceptions.base_exceptions import (
    CreateError,
    DomainError,
    NotFoundError,
    ServerError,
)


class StartVisitorSessionUseCase:
    """
    Entry point of the visitor flow. Resolves the organization, upserts the
    visitor, opens a new session (and its landing page visit), then publishes the
    live presence snapshot to Redis and to the organization's agents.
    """

    def __init__(
        self,
        organization_reader: OrganizationReader,
        visitor_domain_service: VisitorDomainService,
        visitor_session_domain_service: VisitorSessionDomainService,
        visitor_page_visit_domain_service: VisitorPageVisitDomainService,
        presence_store: IVisitorPresenceStore,
        presence_notifier: IVisitorPresenceNotifier,
    ):
        self.organization_reader = organization_reader
        self.visitor_domain_service = visitor_domain_service
        self.visitor_session_domain_service = visitor_session_domain_service
        self.visitor_page_visit_domain_service = visitor_page_visit_domain_service
        self.presence_store = presence_store
        self.presence_notifier = presence_notifier

    async def execute(
        self,
        payload: StartSessionRequestSchema,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        """Execute the session-start flow."""
        try:
            organization = await self.organization_reader.get_organization_by_uuid(
                payload.organization_uuid
            )
            if not organization or organization.id is None:
                raise NotFoundError(error="Organization not found")

            organization_id = organization.id

            visitor = await self.visitor_domain_service.upsert_visitor(
                organization_id=organization_id,
                external_id=payload.visitor_uuid,
            )
            if visitor.id is None:
                raise CreateError(error="Failed to resolve visitor")

            session = await self.visitor_session_domain_service.start_session(
                organization_id=organization_id,
                visitor_id=visitor.id,
                ip_address=ip_address,
                user_agent=user_agent,
                referer=payload.referrer,
                landing_page=payload.page,
            )
            if session.id is None:
                raise CreateError(error="Failed to start session")

            if payload.page:
                await self.visitor_page_visit_domain_service.enter_page(
                    organization_id=organization_id,
                    session_id=session.id,
                    visitor_id=visitor.id,
                    url=payload.page,
                    page_title=None,
                )

            device, browser = parse_user_agent(user_agent)

            presence = VisitorPresence(
                organization_id=organization_id,
                visitor_id=visitor.id,
                visitor_uuid=visitor.uuid,
                session_uuid=session.uuid,
                status="active",
                last_seen=datetime.now(UTC).isoformat(),
                page=payload.page,
                name=visitor.name,
                email=visitor.email,
                phone=visitor.phone,
                external_id=visitor.external_id,
                visit_count=visitor.visit_count,
                is_identified=visitor.is_identified,
                device=device,
                browser=browser,
                ip_address=ip_address,
                active_duration=0,
            )
            await self._publish_presence(presence, session.uuid)

            await self.presence_notifier.notify(
                organization_id,
                {"type": EVENT_SESSION_STARTED, "visitor": presence.to_dict()},
            )

            return {
                "session_uuid": session.uuid,
                "visitor_uuid": visitor.uuid,
                "status": session.status,
                "visit_count": visitor.visit_count,
            }
        except DomainError:
            raise
        except Exception as error:
            raise ServerError(
                error="Failed to start visitor session", internal_details=str(error)
            ) from error

    async def _publish_presence(
        self, presence: VisitorPresence, session_uuid: str
    ) -> None:
        await self.presence_store.set_presence(presence, PRESENCE_TTL_SECONDS)
        await self.presence_store.set_session_index(
            session_uuid=session_uuid,
            organization_id=presence.organization_id,
            visitor_id=presence.visitor_id,
            ttl=PRESENCE_TTL_SECONDS,
        )
