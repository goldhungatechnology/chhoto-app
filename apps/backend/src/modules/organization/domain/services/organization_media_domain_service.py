from src.modules.organization.domain.entities.organization_media_entity import (
    OrganizationMediaEntity,
)
from src.modules.organization.domain.events.organization_media_domain_events import (
    OrganizationMediaCreatedEvent,
    OrganizationMediaUpdatedEvent,
)
from src.modules.organization.domain.repositories.organization_media_repository import (
    IOrganizationMediaRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    CreateError,
    DomainError,
    InvalidError,
    ServerError,
)


class OrganizationMediaDomainService:
    """
    Service class for organization media domain logic.
    """

    def __init__(self, repository: IOrganizationMediaRepository):
        self.repository = repository

    async def create_organization_media(
        self,
        media_entity: OrganizationMediaEntity,
        actor_id: int,
    ) -> OrganizationMediaEntity:
        """
        Creates organization media/contact details.
        """
        try:
            existing_media = await self.repository.get_by(
                organization_id=media_entity.organization_id
            )
            if existing_media:
                raise ConflictError(
                    error="Organization media already exists for this organization"
                )

            created_media = await self.repository.add(media_entity)

            if not created_media or not created_media.id:
                raise ServerError(error="Failed to create organization media")

            created_media.add_event(
                OrganizationMediaCreatedEvent(
                    actor_id=actor_id,
                    organization_id=created_media.organization_id,
                    organization_media_id=created_media.id,
                    session=self.repository.session,
                )
            )

            return created_media

        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to create organization media",
                internal_details=str(e),
            ) from e

    async def get_organization_media(
        self,
        organization_id: int,
    ) -> OrganizationMediaEntity | None:
        """
        Retrieves organization media/contact details by organization ID.
        """
        return await self.repository.get_by(organization_id=organization_id)

    async def update_organization_media(
        self,
        media_entity: OrganizationMediaEntity,
        actor_id: int,
    ) -> OrganizationMediaEntity:
        """
        Updates organization media/contact details.
        """
        try:
            existing_media = await self.repository.get_by(id=media_entity.id)

            if not existing_media:
                raise InvalidError("Organization media not found")

            updated_media = await self.repository.update(media_entity)

            if not updated_media or not updated_media.id:
                raise ServerError(error="Failed to update organization media")

            updated_media.add_event(
                OrganizationMediaUpdatedEvent(
                    actor_id=actor_id,
                    organization_id=updated_media.organization_id,
                    organization_media_id=updated_media.id,
                    session=self.repository.session,
                )
            )

            return updated_media

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to update organization media",
                internal_details=str(e),
            ) from e
