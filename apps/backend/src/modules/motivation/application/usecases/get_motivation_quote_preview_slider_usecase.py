from src.modules.motivation.domain.entities.motivation_quote_entity import (
    MotivationQuoteEntity,
)
from src.modules.motivation.domain.services.motivation_quote_domain_service import (
    MotivationQuoteDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class GetMotivationQuotePreviewSliderUseCase:
    """
    Use case for getting motivation quotes for preview/slider.

    Logic:
    - Return up to 3 active custom quotes if organization has custom quotes.
    - If no custom quotes are available, return up to 3 active system quotes.
    """

    def __init__(
        self,
        motivation_quote_domain_service: MotivationQuoteDomainService,
    ):
        self.motivation_quote_domain_service = motivation_quote_domain_service

    async def execute(
        self,
        organization_id: int,
    ) -> list[MotivationQuoteEntity]:
        try:
            return await self.motivation_quote_domain_service.get_preview_slider_quotes(
                organization_id=organization_id,
                limit=3,
            )

        except DomainError:
            raise

        except Exception as e:
            raise ServerError(
                error="An error occurred while getting motivation quote preview slider",
                internal_details=str(e),
            ) from e
