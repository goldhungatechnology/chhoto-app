from src.modules.links.domain.entities.link_entity import LinkEntity
from src.modules.links.domain.services.link_domain_service import LinkDomainService
from src.shared.exceptions.base_exceptions import (
    DomainError,
    NotFoundError,
    ServerError,
)


class UpdateLinkUseCase:
    """
    Use case for updating a link.
    """

    def __init__(self, link_domain_service: LinkDomainService):
        self.link_domain_service = link_domain_service

    async def execute(
        self, link_uuid: str, user_id: int, title: str | None
    ) -> LinkEntity:
        """
        Execute the use case to update a link title.
        """
        try:
            link = await self.link_domain_service.get_link_by_uuid(link_uuid)
            if not link or link.user_id != user_id:
                raise NotFoundError(error="Link not found")

            link.title = title
            return await self.link_domain_service.update_link(link)
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while updating the link",
                internal_details=str(e),
            ) from e
