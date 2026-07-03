from abc import abstractmethod

from src.modules.motivation.domain.entities.motivation_quote_reaction_entity import (
    MotivationQuoteReactionEntity,
)
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IMotivationQuoteReactionRepository(
    IBaseRepository[MotivationQuoteReactionEntity]
):
    """
    Interface for motivation quote reaction repository.
    """

    @abstractmethod
    async def get_by_member_and_quote(
        self,
        organization_id: int,
        member_id: int,
        quote_id: int,
    ) -> MotivationQuoteReactionEntity | None:
        """
        Get reaction by organization, member and quote.
        """
        pass

    @abstractmethod
    async def list_by_quote_id(
        self,
        organization_id: int,
        quote_id: int,
    ) -> list[MotivationQuoteReactionEntity]:
        """
        List reactions of a quote id.
        """
        pass
