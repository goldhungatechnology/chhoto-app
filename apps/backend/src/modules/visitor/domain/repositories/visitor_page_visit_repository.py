from abc import abstractmethod

from src.modules.visitor.domain.entities.visitor_page_visit_entity import (
    VisitorPageVisitEntity,
)
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IVisitorPageVisitRepository(IBaseRepository[VisitorPageVisitEntity]):
    """
    Interface for the visitor page-visit repository.
    """

    @abstractmethod
    async def get_open_visit(self, session_id: int) -> VisitorPageVisitEntity | None:
        """
        Fetch the currently-open page visit for a session (the most recent row
        whose ``left_at`` is ``NULL``), or ``None`` when no page is open.
        """
