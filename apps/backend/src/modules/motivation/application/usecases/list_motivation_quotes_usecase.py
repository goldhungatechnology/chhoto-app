from src.modules.motivation.domain.entities.motivation_quote_entity import (
    MotivationQuoteEntity,
)
from src.modules.motivation.domain.services.motivation_quote_domain_service import (
    MotivationQuoteDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class ListMotivationQuotesUseCase:
    """
    Use case for listing custom motivation quotes.
    """

    def __init__(
        self,
        motivation_quote_domain_service: MotivationQuoteDomainService,
    ):
        self.motivation_quote_domain_service = motivation_quote_domain_service

    async def execute(
        self,
        organization_id: int,
        status: str | None = None,
        search: str | None = None,
    ) -> list[MotivationQuoteEntity]:
        """
        Execute the use case.
        """
        try:
            return await self.motivation_quote_domain_service.list_custom_quotes(
                organization_id=organization_id,
                status=status,
                search=search,
            )
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while listing motivation quotes",
                internal_details=str(e),
            ) from e
