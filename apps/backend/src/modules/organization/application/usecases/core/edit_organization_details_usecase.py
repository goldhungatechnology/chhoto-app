from src.modules.organization.domain.entities.organization_entity import (
    OrganizationEntity,
)
from src.modules.organization.domain.entities.organization_media_entity import (
    OrganizationMediaEntity,
)
from src.modules.organization.domain.services.organization_domain_service import (
    OrganizationDomainService,
)
from src.modules.organization.domain.services.organization_media_domain_service import (
    OrganizationMediaDomainService,
)
from src.modules.organization.presentation.schemas.organization_schemas import (
    EditOrganizationRequestSchema,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError
from src.shared.mediator.mediator import mediator

# Payload fields that belong to organization media rather than the organization.
MEDIA_FIELDS = (
    "whatsapp",
    "linkedin",
    "email",
    "phone_number",
    "messenger",
    "instagram",
    "twitter",
    "telegram",
)


class EditOrganizationDetailsUseCase:
    """
    Use case for editing an organization and its media/contact details together
    in a single request.
    """

    def __init__(
        self,
        organization_domain_service: OrganizationDomainService,
        organization_media_domain_service: OrganizationMediaDomainService,
    ):
        self.organization_domain_service = organization_domain_service
        self.organization_media_domain_service = organization_media_domain_service

    async def execute(
        self,
        organization_uuid: str,
        payload: EditOrganizationRequestSchema,
        actor_id: int,
    ) -> tuple[OrganizationEntity, OrganizationMediaEntity | None]:
        """
        Applies the organization changes and upserts its media, returning both
        so the API layer can serialize them in a single response. Only the
        fields present in the payload are touched.
        """
        try:
            organization = (
                await self.organization_domain_service.get_organization_by_uuid(
                    organization_uuid
                )
            )
            if not organization or organization.id is None:
                raise ServerError(
                    error="Error while retrieving organization details",
                    internal_details=f"No organization found with uuid {organization_uuid}",
                )
            organization_id = organization.id

            fields = payload.model_dump(exclude_unset=True)
            org_fields = {k: v for k, v in fields.items() if k not in MEDIA_FIELDS}
            media_fields = {k: v for k, v in fields.items() if k in MEDIA_FIELDS}

            organization = await self._apply_organization_changes(
                organization, org_fields, actor_id
            )
            media = await self._upsert_media(organization_id, media_fields, actor_id)

            return organization, media

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                "Failed to edit organization details",
                internal_details=str(e),
            ) from e

    async def _apply_organization_changes(
        self,
        organization: OrganizationEntity,
        org_fields: dict,
        actor_id: int,
    ) -> OrganizationEntity:
        """
        Updates the organization's core fields. Returns the organization
        unchanged when there is nothing to update.
        """
        if not org_fields:
            return organization

        if "name" in org_fields:
            await self.organization_domain_service.ensure_name_available(
                name=org_fields["name"], exclude_id=organization.id
            )

        for key, value in org_fields.items():
            setattr(organization, key, value)

        updated_organization = (
            await self.organization_domain_service.update_organization(
                organization, actor_id
            )
        )

        for event in updated_organization.pull_events():
            await mediator.publish(event)

        return updated_organization

    async def _upsert_media(
        self,
        organization_id: int,
        media_fields: dict,
        actor_id: int,
    ) -> OrganizationMediaEntity | None:
        """
        Creates or updates the organization's media. When no media fields are
        provided, returns the existing media untouched so it can still be
        included in the response.
        """
        existing_media = (
            await self.organization_media_domain_service.get_organization_media(
                organization_id=organization_id
            )
        )

        if not media_fields:
            return existing_media

        if existing_media:
            for key, value in media_fields.items():
                setattr(existing_media, key, value)
            existing_media.updated_by_id = actor_id

            updated_media = (
                await self.organization_media_domain_service.update_organization_media(
                    media_entity=existing_media,
                    actor_id=actor_id,
                )
            )
            for event in updated_media.pull_events():
                await mediator.publish(event)
            return updated_media

        new_media = OrganizationMediaEntity(
            organization_id=organization_id,
            whatsapp=media_fields.get("whatsapp"),
            linkedin=media_fields.get("linkedin"),
            email=media_fields.get("email"),
            phone_number=media_fields.get("phone_number"),
            messenger=media_fields.get("messenger"),
            instagram=media_fields.get("instagram"),
            twitter=media_fields.get("twitter"),
            telegram=media_fields.get("telegram"),
            created_by_id=actor_id,
        )
        created_media = (
            await self.organization_media_domain_service.create_organization_media(
                media_entity=new_media,
                actor_id=actor_id,
            )
        )
        for event in created_media.pull_events():
            await mediator.publish(event)
        return created_media
