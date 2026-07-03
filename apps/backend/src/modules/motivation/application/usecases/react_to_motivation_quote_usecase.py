from src.modules.motivation.domain.entities.motivation_quote_reaction_entity import (
    MotivationQuoteReactionEntity,
)
from src.modules.motivation.domain.services.motivation_quote_reaction_domain_service import (
    MotivationQuoteReactionDomainService,
)
from src.modules.motivation.presentation.schemas.motivation_schemas import (
    ReactToMotivationQuoteRequestSchema,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class ReactToMotivationQuoteUseCase:
    """
    Use case for reacting to a motivation quote.
    """

    def __init__(
        self,
        motivation_quote_reaction_domain_service: MotivationQuoteReactionDomainService,
    ):
        self.motivation_quote_reaction_domain_service = (
            motivation_quote_reaction_domain_service
        )

    async def execute(
        self,
        payload: ReactToMotivationQuoteRequestSchema,
        organization_id: int,
        member_id: int,
        actor_id: int,
    ) -> MotivationQuoteReactionEntity:
        """
        Execute the use case.
        """
        try:
            return await self.motivation_quote_reaction_domain_service.add_or_update_reaction(
                organization_id=organization_id,
                member_id=member_id,
                quote_uuid=payload.quote_uuid,
                reaction_type=payload.reaction_type,
                actor_id=actor_id,
            )
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while reacting to motivation quote",
                internal_details=str(e),
            ) from e
