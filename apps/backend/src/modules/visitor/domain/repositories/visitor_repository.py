from abc import abstractmethod

from src.modules.visitor.domain.entities.visitor_entity import VisitorEntity
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IVisitorRepository(IBaseRepository[VisitorEntity]):
    """
    Interface for the visitor repository.
    """

    @abstractmethod
    async def get_by_external_id(
        self, organization_id: int, external_id: str
    ) -> VisitorEntity | None:
        """
        Fetch a visitor by its organization-scoped external id (the SDK
        ``visitor_uuid``). Returns ``None`` when no such visitor exists.
        """
