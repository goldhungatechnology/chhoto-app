from src.modules.visitor.domain.constants import EVENT_SESSION_ENDED
from src.modules.visitor.domain.ports.visitor_presence_notifier import (
    IVisitorPresenceNotifier,
)
from src.modules.visitor.domain.ports.visitor_presence_store import (
    IVisitorPresenceStore,
)
from src.modules.visitor.domain.services.visitor_page_visit_domain_service import (
    VisitorPageVisitDomainService,
)
from src.modules.visitor.domain.services.visitor_session_domain_service import (
    VisitorSessionDomainService,
)
from src.modules.visitor.presentation.schemas.visitor_schemas import (
    EndSessionRequestSchema,
)
from src.shared.exceptions.base_exceptions import (
    DomainError,
    InvalidError,
    ServerError,
)


class EndVisitorSessionUseCase:
    """
    Terminates a session: closes the last open page visit, marks the session
    ended in the database, and clears the visitor's live presence. Idempotent —
    ending an already-ended session simply clears presence again.
    """

    def __init__(
        self,
        visitor_session_domain_service: VisitorSessionDomainService,
        visitor_page_visit_domain_service: VisitorPageVisitDomainService,
        presence_store: IVisitorPresenceStore,
        presence_notifier: IVisitorPresenceNotifier,
    ):
        self.visitor_session_domain_service = visitor_session_domain_service
        self.visitor_page_visit_domain_service = visitor_page_visit_domain_service
        self.presence_store = presence_store
        self.presence_notifier = presence_notifier

    async def execute(self, payload: EndSessionRequestSchema) -> dict:
        """Execute the session-end flow."""
        try:
            session = await self.visitor_session_domain_service.get_session_by_uuid(
                payload.session_uuid
            )
            if not session or session.id is None:
                raise InvalidError(error="Session not found")

            if not session.is_ended():
                await self.visitor_page_visit_domain_service.close_open_page(session.id)
                await self.visitor_session_domain_service.end_session(session)

            await self.presence_store.delete_presence(
                organization_id=session.organization_id,
                visitor_id=session.visitor_id,
            )
            await self.presence_store.delete_session_index(session.uuid)

            await self.presence_notifier.notify(
                session.organization_id,
                {
                    "type": EVENT_SESSION_ENDED,
                    "session_uuid": session.uuid,
                    "visitor_id": session.visitor_id,
                },
            )

            return {"session_uuid": session.uuid, "status": "ended"}
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to end visitor session", internal_details=str(e)
            ) from e
