from src.modules.links.domain.entities.link_session_entity import LinkSessionEntity
from src.modules.links.domain.repositories.link_session_repository import (
    ILinkSessionRepository,
)
from src.shared.exceptions.base_exceptions import CreateError


class LinkSessionDomainService:
    """
    Service class for link session domain logic.
    """

    def __init__(self, repository: ILinkSessionRepository):
        self.repository = repository

    async def create_link_session(
        self, session_entity: LinkSessionEntity
    ) -> LinkSessionEntity:
        try:
            return await self.repository.add(session_entity)
        except Exception as e:
            raise CreateError(
                error="Failed to create link session", internal_details=str(e)
            ) from e

    async def list_sessions_by_link_id(self, link_id: int) -> list[LinkSessionEntity]:
        try:
            return await self.repository.filter(link_id=link_id)
        except Exception as e:
            raise CreateError(
                error="Failed to list link sessions", internal_details=str(e)
            ) from e
