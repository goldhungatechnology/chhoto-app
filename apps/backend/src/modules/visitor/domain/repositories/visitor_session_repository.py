from src.modules.visitor.domain.entities.visitor_session_entity import (
    VisitorSessionEntity,
)
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IVisitorSessionRepository(IBaseRepository[VisitorSessionEntity]):
    """
    Interface for the visitor session repository. Sessions are looked up by their
    public ``uuid`` (the SDK ``session_uuid``) via the inherited ``get_by_uuid``.
    """
