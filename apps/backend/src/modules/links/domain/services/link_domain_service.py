from src.modules.links.domain.entities.link_entity import LinkEntity
from src.modules.links.domain.repositories.link_repository import ILinkRepository
from src.shared.exceptions.base_exceptions import CreateError, ServerError


class LinkDomainService:
    """
    Service class for link domain logic.
    """

    def __init__(self, repository: ILinkRepository):
        self.repository = repository

    async def create_link(self, link_entity: LinkEntity) -> LinkEntity:
        """
        Create a new link entity in the repository.
        """
        try:
            return await self.repository.add(link_entity)
        except Exception as e:
            raise CreateError(
                error="Failed to create link", internal_details=str(e)
            ) from e

    async def get_link_by_uuid(self, link_uuid: str) -> LinkEntity | None:
        """
        Retrieve a link entity by its UUID from the repository.
        """
        try:
            return await self.repository.get_by_uuid(link_uuid)
        except Exception as e:
            raise ServerError(
                error="Failed to retrieve link", internal_details=str(e)
            ) from e

    async def get_link_by_short_url(self, short_url: str) -> LinkEntity | None:
        """
        Retrieve a link entity by its short URL from the repository.
        """
        try:
            return await self.repository.get_by(short_url=short_url)
        except Exception as e:
            raise ServerError(
                error="Failed to retrieve link by short url", internal_details=str(e)
            ) from e

    async def list_links_by_user_id(self, user_id: int) -> list[LinkEntity]:
        """
        List all link entities associated with a specific user ID from the repository.
        """
        try:
            return await self.repository.filter(user_id=user_id)
        except Exception as e:
            raise ServerError(
                error="Failed to list links", internal_details=str(e)
            ) from e

    async def update_link(self, link_entity: LinkEntity) -> LinkEntity:
        """
        Update an existing link entity in the repository.
        """
        try:
            return await self.repository.update(link_entity)
        except Exception as e:
            raise ServerError(
                error="Failed to update link", internal_details=str(e)
            ) from e
