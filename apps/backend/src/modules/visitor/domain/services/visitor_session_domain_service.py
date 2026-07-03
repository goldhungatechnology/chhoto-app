from src.modules.visitor.domain.entities.visitor_session_entity import (
    VisitorSessionEntity,
)
from src.modules.visitor.domain.repositories.visitor_session_repository import (
    IVisitorSessionRepository,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class VisitorSessionDomainService:
    """
    Domain service for the visitor-session lifecycle.
    """

    def __init__(self, repository: IVisitorSessionRepository):
        self.repository = repository

    async def start_session(
        self,
        *,
        organization_id: int,
        visitor_id: int,
        ip_address: str | None = None,
        user_agent: str | None = None,
        referer: str | None = None,
        landing_page: str | None = None,
    ) -> VisitorSessionEntity:
        """Create and persist a fresh active session for a visitor."""
        session = VisitorSessionEntity(
            organization_id=organization_id,
            visitor_id=visitor_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
            landing_page=landing_page,
        )
        try:
            return await self.repository.add(session)
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to start visitor session", internal_details=str(e)
            ) from e

    async def get_session_by_uuid(
        self, session_uuid: str
    ) -> VisitorSessionEntity | None:
        """Fetch a session by its public uuid (the SDK ``session_uuid``)."""
        return await self.repository.get_by_uuid(session_uuid)

    async def end_session(self, session: VisitorSessionEntity) -> VisitorSessionEntity:
        """Terminate a session (idempotent) and persist."""
        if session.is_ended():
            return session
        try:
            session.end()
            return await self.repository.update(session)
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to end visitor session", internal_details=str(e)
            ) from e
