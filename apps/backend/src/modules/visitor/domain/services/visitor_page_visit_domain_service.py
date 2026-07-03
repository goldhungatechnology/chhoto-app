from src.modules.visitor.domain.entities.visitor_page_visit_entity import (
    VisitorPageVisitEntity,
)
from src.modules.visitor.domain.repositories.visitor_page_visit_repository import (
    IVisitorPageVisitRepository,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class VisitorPageVisitDomainService:
    """
    Domain service for page-visit tracking within a session.
    """

    def __init__(self, repository: IVisitorPageVisitRepository):
        self.repository = repository

    async def enter_page(
        self,
        *,
        organization_id: int,
        session_id: int,
        visitor_id: int,
        url: str,
        page_title: str | None = None,
    ) -> VisitorPageVisitEntity:
        """
        Record a page entry: close the currently-open page visit (if any) and
        open a new one. The two writes happen in the caller's unit of work so
        they commit atomically.
        """
        try:
            await self.close_open_page(session_id)

            page_visit = VisitorPageVisitEntity(
                organization_id=organization_id,
                session_id=session_id,
                visitor_id=visitor_id,
                url=url,
                page_title=page_title,
            )
            return await self.repository.add(page_visit)
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to record page visit", internal_details=str(e)
            ) from e

    async def close_open_page(self, session_id: int) -> VisitorPageVisitEntity | None:
        """
        Close the open page visit for a session, if one exists. Returns the
        closed entity, or ``None`` when nothing was open.
        """
        open_visit = await self.repository.get_open_visit(session_id)
        if not open_visit:
            return None
        open_visit.close()
        return await self.repository.update(open_visit)
