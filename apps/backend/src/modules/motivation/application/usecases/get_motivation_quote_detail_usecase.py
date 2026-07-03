from src.modules.motivation.domain.entities.motivation_quote_entity import (
    MotivationQuoteEntity,
)
from src.modules.motivation.domain.services.motivation_quote_domain_service import (
    MotivationQuoteDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class GetMotivationQuoteDetailUseCase:
    """
    Use case for retrieving a motivation quote by id.
    """

    def __init__(
        self,
        motivation_quote_domain_service: MotivationQuoteDomainService,
    ):
        self.motivation_quote_domain_service = motivation_quote_domain_service

    async def execute(
        self,
        quote_uuid: str,
        organization_id: int,
    ) -> MotivationQuoteEntity:
        """
        Execute the use case.
        """
        try:
            return await self.motivation_quote_domain_service.get_quote_by_uuid(
                quote_uuid=quote_uuid,
                organization_id=organization_id,
            )

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while retrieving motivation quote",
                internal_details=str(e),
            ) from e
