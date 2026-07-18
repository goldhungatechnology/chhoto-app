import uuid

from fastapi.requests import Request

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


class RedirectLinkUseCase:
    """
    Use case for redirecting a short URL to its destination
    and recording the click as a link session.
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
        short_url: str,
        request: Request,
    ) -> str:
        """
        Resolve a short URL, increment click count, record the visit session,
        and return the destination URL for redirection.
        """
        try:
            link = await self.link_domain_service.get_link_by_short_url(short_url)

            if not link:
                raise NotFoundError(
                    error="Short URL not found",
                    errors={"short_url": "This short URL does not exist"},
                )

            if link.is_expired():
                raise NotFoundError(
                    error="Link has expired",
                    errors={"short_url": "This link has expired"},
                )

            link.increment_clicks()
            await self.link_domain_service.update_link(link)

            session_entity = LinkSessionEntity(
                uuid=str(uuid.uuid4()),
                link_id=link.id,
                ip_address=request.state.ip_address,
                device=request.state.device,
                browser=request.state.browser,
                referral_source=request.headers.get("referer"),
            )
            await self.link_session_domain_service.create_link_session(session_entity)

            return link.destination_url

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while resolving the link",
                internal_details=str(e),
            ) from e
