from src.modules.links.domain.entities.link_session_entity import LinkSessionEntity
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class ILinkSessionRepository(IBaseRepository[LinkSessionEntity]):
    """
    Interface for the Link Session repository.
    """
