import uuid

from chhoto_encoding import encode

from src.modules.links.domain.entities.link_entity import LinkEntity
from src.modules.links.domain.services.link_domain_service import LinkDomainService
from src.modules.links.presentation.schemas.link_schemas import CreateLinkRequestSchema
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    DomainError,
    ServerError,
)


class CreateLinkUseCase:
    """
    Use case for creating a new short link.
    """

    def __init__(self, link_domain_service: LinkDomainService):
        self.link_domain_service = link_domain_service

    async def execute(
        self,
        payload: CreateLinkRequestSchema,
        user_id: int,
    ) -> LinkEntity:
        """
        Execute the use case to create a new short link.
        """
        try:
            entity_uuid = uuid.uuid4()
            short_url = payload.custom_slug or self._generate_short_url(
                value=entity_uuid.int
            )

            if await self.link_domain_service.get_link_by_short_url(short_url):
                raise ConflictError(
                    error="Short URL already exists",
                    errors={"short_url": "This short URL is already taken"},
                )

            link = LinkEntity(
                uuid=str(entity_uuid),
                user_id=user_id,
                destination_url=str(payload.destination_url),
                short_url=short_url,
                tags=payload.tags,
                auto_expire=payload.auto_expire,
                title=payload.title,
            )

            return await self.link_domain_service.create_link(link)

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while creating the link",
                internal_details=str(e),
            ) from e

    @staticmethod
    def _generate_short_url(value: int) -> str:
        """
        Generate a short URL using the chhoto_encoding library.

        Args:
            value (int): The integer value to encode.

        Returns:
            str: The generated short URL.
        """
        return encode(value)
