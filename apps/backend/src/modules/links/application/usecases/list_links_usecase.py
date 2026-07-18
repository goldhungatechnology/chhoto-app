from src.modules.links.domain.entities.link_entity import LinkEntity
from src.modules.links.domain.services.link_domain_service import LinkDomainService
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class ListLinksUseCase:
    """
    Use case for listing all links for a user.
    """

    def __init__(self, link_domain_service: LinkDomainService):
        self.link_domain_service = link_domain_service

    async def execute(self, user_id: int) -> list[LinkEntity]:
        """
        Execute the use case to list all links for a user.
        """
        try:
            return await self.link_domain_service.list_links_by_user_id(user_id)
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while listing links",
                internal_details=str(e),
            ) from e
