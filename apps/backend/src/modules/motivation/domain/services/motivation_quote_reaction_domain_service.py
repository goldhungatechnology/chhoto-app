from src.modules.motivation.domain.entities.motivation_quote_reaction_entity import (
    MotivationQuoteReactionEntity,
)
from src.modules.motivation.domain.events.motivation_domain_events import (
    MotivationQuoteReactionAddedOrUpdatedEvent,
)
from src.modules.motivation.domain.repositories.daily_motivation_config_repository import (
    IDailyMotivationConfigRepository,
)
from src.modules.motivation.domain.repositories.motivation_quote_reaction_repository import (
    IMotivationQuoteReactionRepository,
)
from src.modules.motivation.domain.repositories.motivation_quote_repository import (
    IMotivationQuoteRepository,
)
from src.shared.exceptions.base_exceptions import (
    CreateError,
    DomainError,
    InvalidError,
)


class MotivationQuoteReactionDomainService:
    """
    Service class for motivation quote reaction domain logic.
    """

    def __init__(
        self,
        reaction_repository: IMotivationQuoteReactionRepository,
        quote_repository: IMotivationQuoteRepository,
        config_repository: IDailyMotivationConfigRepository,
    ):
        self.reaction_repository = reaction_repository
        self.quote_repository = quote_repository
        self.config_repository = config_repository

    async def add_or_update_reaction(
        self,
        organization_id: int,
        member_id: int,
        quote_uuid: str,
        reaction_type: str,
        actor_id: int,
    ) -> MotivationQuoteReactionEntity:
        """
        Adds or updates member reaction on a motivation quote.
        """
        try:
            self._validate_reaction_type(reaction_type)

            config = await self.config_repository.get_by_organization_id(
                organization_id=organization_id
            )

            if config and not config.allow_reactions:
                raise InvalidError("Motivation quote reactions are disabled")

            quote = await self.quote_repository.get_reactable_quote_by_uuid(
                organization_id=organization_id,
                quote_uuid=quote_uuid,
            )

            if not quote or quote.id is None:
                raise InvalidError("Motivation quote not found")

            if quote.status != "active":
                raise InvalidError("Cannot react to inactive motivation quote")

            existing_reaction = await self.reaction_repository.get_by_member_and_quote(
                organization_id=organization_id,
                member_id=member_id,
                quote_id=quote.id,
            )

            if existing_reaction:
                existing_reaction.reaction_type = reaction_type
                existing_reaction.updated_by_id = actor_id
                existing_reaction.mark_updated()

                saved_reaction = await self.reaction_repository.update(
                    existing_reaction
                )
            else:
                reaction_entity = MotivationQuoteReactionEntity(
                    organization_id=organization_id,
                    member_id=member_id,
                    quote_id=quote.id,
                    reaction_type=reaction_type,
                    created_by_id=actor_id,
                )

                saved_reaction = await self.reaction_repository.add(reaction_entity)

            if not saved_reaction.id:
                raise CreateError(error="Failed to save motivation quote reaction")

            saved_reaction.add_event(
                MotivationQuoteReactionAddedOrUpdatedEvent(
                    actor_id=actor_id,
                    organization_id=organization_id,
                    member_id=member_id,
                    quote_uuid=quote.uuid,
                    reaction_id=saved_reaction.id,
                    reaction_type=reaction_type,
                    session=self.reaction_repository.session,
                )
            )

            return saved_reaction

        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to add or update motivation quote reaction",
                internal_details=str(e),
            ) from e

    async def list_quote_reactions(
        self,
        organization_id: int,
        quote_uuid: str,
    ) -> list[MotivationQuoteReactionEntity]:
        """
        Lists reactions of a motivation quote.
        """
        quote = await self.quote_repository.get_reactable_quote_by_uuid(
            organization_id=organization_id,
            quote_uuid=quote_uuid,
        )

        if not quote or quote.id is None:
            raise InvalidError("Motivation quote not found")

        return await self.reaction_repository.list_by_quote_id(
            organization_id=organization_id,
            quote_id=quote.id,
        )

    def _validate_reaction_type(self, reaction_type: str) -> None:
        """
        Validate reaction type.
        """
        if not reaction_type or not reaction_type.strip():
            raise InvalidError("Reaction type is required")
