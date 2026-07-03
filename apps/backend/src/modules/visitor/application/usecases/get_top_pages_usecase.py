from src.modules.visitor.domain.repositories.visitor_page_visit_repository import (
    IVisitorPageVisitRepository,
)
from src.modules.visitor.domain.repositories.visitor_repository import (
    IVisitorRepository,
)
from src.modules.visitor.domain.value_objects.top_pages_report import TopPagesReport


class GetTopPagesUseCase:
    """
    Use case to fetch the most visited pages in the organization.
    """

    TOP_N = 5

    def __init__(
        self,
        visitor_repository: IVisitorRepository,
        visitor_page_visit_repository: IVisitorPageVisitRepository,
    ):
        self.visitor_repository = visitor_repository
        self.visitor_page_visit_repository = visitor_page_visit_repository

    async def execute(self, organization_id: int) -> dict:
        """
        Executes the use case to query visitor page visits and construct the top pages report.
        """
        visitors = await self.visitor_repository.filter(organization_id=organization_id)
        total_visitors = len(visitors)

        if total_visitors == 0:
            return {"total": 0, "pages": []}

        page_visits = await self.visitor_page_visit_repository.filter(
            organization_id=organization_id
        )

        report = TopPagesReport.generate(
            page_visits=page_visits,
            total_visitors=total_visitors,
            limit=self.TOP_N,
        )

        return report.to_dict()
