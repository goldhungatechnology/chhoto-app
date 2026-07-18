from src.modules.links.domain.entities.link_entity import LinkEntity
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class ILinkRepository(IBaseRepository[LinkEntity]):
    """
    Interface for the Link repository.
    """
