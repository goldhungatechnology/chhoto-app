from src.modules.links.domain.entities.link_session_entity import LinkSessionEntity
from src.modules.links.domain.services.link_domain_service import LinkDomainService
from src.modules.links.domain.services.link_session_domain_service import (
    LinkSessionDomainService,
)
from src.shared.exceptions.base_exceptions import (
    DomainError,
    NotFoundError,
    ServerError,
)


class ListLinkSessionsUseCase:
    """
    Use case for listing all sessions (clicks) for a specific link by its UUID.
    """

    def __init__(
        self,
        link_domain_service: LinkDomainService,
        link_session_domain_service: LinkSessionDomainService,
    ):
        self.link_domain_service = link_domain_service
        self.link_session_domain_service = link_session_domain_service

    async def execute(
        self,
        link_uuid: str,
        user_id: int,
    ) -> list[LinkSessionEntity]:
        """
        Execute the use case to list all sessions for a given link UUID.

        1. Resolves the link UUID to a link entity and verifies ownership.
        2. Retrieves all sessions associated with that link's ID.
        """
        try:
            link = await self.link_domain_service.get_link_by_uuid(link_uuid)

            if not link or not link.id:
                raise NotFoundError(
                    error="Link not found",
                    errors={"link_uuid": "No link found with the given UUID"},
                )

            if link.user_id != user_id:
                raise NotFoundError(
                    error="Link not found",
                    errors={"link_uuid": "No link found with the given UUID"},
                )

            return await self.link_session_domain_service.list_sessions_by_link_id(
                link.id
            )
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while listing link sessions",
                internal_details=str(e),
            ) from e
