from src.modules.motivation.domain.entities.motivation_quote_entity import (
    MotivationQuoteEntity,
)
from src.modules.motivation.domain.enums.motivation_enums import QuotesStatusEnum
from src.modules.motivation.domain.services.motivation_quote_domain_service import (
    MotivationQuoteDomainService,
)
from src.modules.motivation.presentation.schemas.motivation_schemas import (
    CreateMotivationQuoteRequestSchema,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class CreateMotivationQuoteUseCase:
    """
    Use case for creating a custom motivation quote.
    """

    def __init__(
        self,
        motivation_quote_domain_service: MotivationQuoteDomainService,
    ):
        self.motivation_quote_domain_service = motivation_quote_domain_service

    async def execute(
        self,
        payload: CreateMotivationQuoteRequestSchema,
        organization_id: int,
        actor_id: int,
    ) -> MotivationQuoteEntity:
        """
        Execute the use case.
        """
        try:
            quote_entity = MotivationQuoteEntity(
                organization_id=organization_id,
                context=payload.context,
                author_name=payload.author_name,
                status=QuotesStatusEnum.ACTIVE,
                font_style=payload.font_style,
                theme_color=payload.theme_color,
                bg_image=payload.bg_image,
                created_by_id=actor_id,
            )

            return await self.motivation_quote_domain_service.create_custom_quote(
                quote_entity=quote_entity,
                actor_id=actor_id,
            )
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while creating motivation quote",
                internal_details=str(e),
            ) from e
