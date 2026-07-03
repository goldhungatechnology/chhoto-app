from abc import abstractmethod

from src.modules.motivation.domain.entities.motivation_quote_entity import (
    MotivationQuoteEntity,
)
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IMotivationQuoteRepository(IBaseRepository[MotivationQuoteEntity]):
    """
    Interface for motivation quote repository.
    """

    @abstractmethod
    async def list_by_organization_id(
        self,
        organization_id: int,
        is_sys_default: bool | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> list[MotivationQuoteEntity]:
        """
        List motivation quotes by organization id.
        """
        pass

    @abstractmethod
    async def get_active_custom_quote(
        self,
        organization_id: int,
    ) -> MotivationQuoteEntity | None:
        """
        Get active custom motivation quote for organization.
        """
        pass

    @abstractmethod
    async def get_active_system_quote(
        self,
    ) -> MotivationQuoteEntity | None:
        """
        Get active system default motivation quote.
        """
        pass

    @abstractmethod
    async def get_reactable_quote(
        self,
        organization_id: int,
        quote_id: int,
    ) -> MotivationQuoteEntity | None:
        """
        Get quote that can be reacted to.

        It allows:
        1. Custom quote of the current organization
        2. Global system/default quote with organization_id NULL
        """
        pass

    @abstractmethod
    async def get_reactable_quote_by_uuid(
        self,
        organization_id: int,
        quote_uuid: str,
    ) -> MotivationQuoteEntity | None:
        """
        Get quote that can be reacted to by uuid.
        """
        pass

    @abstractmethod
    async def list_system_quotes(
        self,
        organization_id: int,
        status: str | None = None,
        search: str | None = None,
    ) -> list[MotivationQuoteEntity]:
        """
        List global system/sample motivation quotes.
        """
        pass

    @abstractmethod
    async def get_system_quote_by_uuid(
        self,
        quote_uuid: str,
    ) -> MotivationQuoteEntity | None:
        """
        Get global system/sample motivation quote by uuid.
        """
        pass

    @abstractmethod
    async def list_active_custom_quotes_for_preview(
        self,
        organization_id: int,
        limit: int = 3,
    ) -> list[MotivationQuoteEntity]:
        """
        List active custom motivation quotes for preview slider.
        """
        pass

    @abstractmethod
    async def list_active_system_quotes_for_preview(
        self,
        limit: int = 3,
    ) -> list[MotivationQuoteEntity]:
        """
        List active system motivation quotes for preview slider.
        """
        pass
