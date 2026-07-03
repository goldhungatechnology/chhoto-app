from src.modules.motivation.domain.entities.motivation_quote_entity import (
    MotivationQuoteEntity,
)
from src.modules.motivation.domain.services.motivation_quote_domain_service import (
    MotivationQuoteDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class GetDailyMotivationQuoteUseCase:
    """
    Use case for getting the quote that should be displayed today.
    """

    def __init__(
        self,
        motivation_quote_domain_service: MotivationQuoteDomainService,
    ):
        self.motivation_quote_domain_service = motivation_quote_domain_service

    async def execute(
        self,
        organization_id: int,
    ) -> MotivationQuoteEntity | None:
        """
        Execute the use case.
        """
        try:
            return await self.motivation_quote_domain_service.get_daily_quote(
                organization_id=organization_id
            )
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while getting daily motivation quote",
                internal_details=str(e),
            ) from e
