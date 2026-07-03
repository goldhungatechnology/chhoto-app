from src.modules.visitor.domain.repositories.visitor_repository import (
    IVisitorRepository,
)
from src.modules.visitor.domain.repositories.visitor_session_repository import (
    IVisitorSessionRepository,
)


class GetVisitorsByCountryUseCase:
    """
    Groups all database visitors by country based on their latest session IP address.
    """

    def __init__(
        self,
        visitor_repository: IVisitorRepository,
        visitor_session_repository: IVisitorSessionRepository,
    ):
        self.visitor_repository = visitor_repository
        self.visitor_session_repository = visitor_session_repository

    async def execute(self, organization_id: int) -> dict:
        """
        Executes the use case to aggregate visitors by country.
        """
        visitors = await self.visitor_repository.filter(organization_id=organization_id)
        total_visitors = len(visitors)

        if total_visitors == 0:
            return {"total": 0, "countries": []}

        # TODO: have to implement the logic of the IP to country address mapping. For now, let's assume all visitors are from Nepal.
        countries_list = [
            {
                "country": "Nepal",
                "count": total_visitors,
                "percentage": 100.0,
            }
        ]

        return {"total": total_visitors, "countries": countries_list}
