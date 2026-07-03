from src.modules.motivation.domain.entities.motivation_quote_entity import (
    MotivationQuoteEntity,
)
from src.modules.motivation.domain.services.motivation_quote_domain_service import (
    MotivationQuoteDomainService,
)
from src.modules.motivation.presentation.schemas.motivation_schemas import (
    UpdateMotivationQuoteRequestSchema,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class UpdateMotivationQuoteUseCase:
    """
    Use case for updating a custom motivation quote.
    """

    def __init__(
        self,
        motivation_quote_domain_service: MotivationQuoteDomainService,
    ):
        self.motivation_quote_domain_service = motivation_quote_domain_service

    async def execute(
        self,
        quote_uuid: str,
        payload: UpdateMotivationQuoteRequestSchema,
        organization_id: int,
        actor_id: int,
    ) -> MotivationQuoteEntity:
        """
        Execute the use case.
        """
        try:
            quote_entity = MotivationQuoteEntity(
                uuid=quote_uuid,
                organization_id=organization_id,
                context=str(payload.context) if payload.context is not None else None,
                author_name=(
                    str(payload.author_name)
                    if payload.author_name is not None
                    else None
                ),
                status=payload.status.value if payload.status is not None else None,
                font_style=(
                    payload.font_style.value if payload.font_style is not None else None
                ),
                theme_color=(
                    str(payload.theme_color)
                    if payload.theme_color is not None
                    else None
                ),
                bg_image=str(payload.bg_image)
                if payload.bg_image is not None
                else None,
                updated_by_id=actor_id,
            )

            return await self.motivation_quote_domain_service.update_custom_quote(
                quote_entity=quote_entity,
                actor_id=actor_id,
            )
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while updating motivation quote",
                internal_details=str(e),
            ) from e
