from src.modules.organization.domain.entities.organization_entity import (
    OrganizationEntity,
)
from src.modules.organization.domain.events.organization_domain_events import (
    OrganizationSwitchedEvent,
    OrganizationUpdatedEvent,
)
from src.modules.organization.domain.repositories.organization_repository import (
    IOrganizationRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    CreateError,
    DomainError,
    InvalidError,
)


class OrganizationDomainService:
    """
    Service class for organization domain logic.
    """

    def __init__(self, repository: IOrganizationRepository):
        self.repository = repository

    async def create_organization(
        self, organization_entity: OrganizationEntity
    ) -> OrganizationEntity:
        """
        Creates a new organization with uniqueness checks.
        """
        try:
            await self._ensure_slug_unique(organization_entity.slug)
            await self._ensure_domain_unique(organization_entity.domain)
            return await self.repository.add(organization_entity)
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to create organization", internal_details=str(e)
            ) from e

    async def get_organization_by_uuid(self, uuid: str) -> OrganizationEntity | None:
        """
        Retrieves an organization by its UUID.
        """
        return await self.repository.get_by(uuid=uuid, deleted_at=None)

    async def get_organization_by_id(
        self, organization_id: int
    ) -> OrganizationEntity | None:
        """
        Retrieves an organization by its ID.
        """
        return await self.repository.get_by(id=organization_id, deleted_at=None)

    async def list_organizations_by_user_id(
        self, user_id: int
    ) -> list[OrganizationEntity] | None:
        """
        Retrieves a list of organizations associated with a user ID.
        """
        return await self.repository.list_by_user_id(user_id=user_id)

    async def switch_organization(
        self, user_id: int, target_organization_uuid: str, current_session_uuid: str
    ) -> OrganizationEntity:
        """
        Switches the user's current organization to the target organization.
        """
        organization = await self.get_organization_by_uuid(target_organization_uuid)
        if not organization:
            raise InvalidError("Organization not found")

        organization.add_event(
            OrganizationSwitchedEvent(
                target_organization_uuid=target_organization_uuid,
                actor_id=user_id,
                session=self.repository.session,
                current_session_uuid=current_session_uuid,
            )
        )

        return organization

    async def update_organization(
        self, organization_entity: OrganizationEntity, actor_id: int
    ) -> OrganizationEntity:
        """
        Updates an existing organization with uniqueness checks.
        """
        try:
            existing_org = await self.repository.get_by(
                id=organization_entity.id, deleted_at=None
            )
            if not existing_org:
                raise InvalidError("Organization not found")

            if (
                organization_entity.slug
                and organization_entity.slug != existing_org.slug
            ):
                await self._ensure_slug_unique(organization_entity.slug)

            if (
                organization_entity.domain
                and organization_entity.domain != existing_org.domain
            ):
                await self._ensure_domain_unique(organization_entity.domain)

            updated_org = await self.repository.update(organization_entity)
            if not updated_org.id:
                raise InvalidError("Organization not found after update")

            updated_org.add_event(
                OrganizationUpdatedEvent(
                    actor_id=actor_id,
                    organization_id=updated_org.id,
                )
            )
            return updated_org
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to update organization", internal_details=str(e)
            ) from e

    async def activate_organization(self, organization_id: int) -> OrganizationEntity:
        """
        Flip a pending organization to active. Called from the create flow
        after all must-succeed provisioning listeners have completed in the
        same transaction.
        """
        try:
            existing_org = await self.repository.get_by(
                id=organization_id, deleted_at=None
            )
            if not existing_org:
                raise InvalidError("Organization not found")

            if existing_org.status == "active":
                return existing_org

            existing_org.status = "active"
            existing_org.mark_updated()

            updated_org = await self.repository.update(existing_org)
            if not updated_org.id:
                raise InvalidError("Organization not found after activation")

            return updated_org
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to activate organization", internal_details=str(e)
            ) from e

    async def ensure_name_available(
        self, name: str, exclude_id: int | None = None
    ) -> None:
        """
        Ensure no other (non-deleted) organization already uses this name.

        Excludes the organization being edited (so re-submitting the same name
        is a no-op) and ignores soft-deleted rows.
        """
        existing_org = await self.repository.get_by(name__ilike=name, deleted_at=None)
        if existing_org and existing_org.id != exclude_id:
            raise InvalidError(
                error="Organization name already exists",
                internal_details=f"An organization with the name '{name}' already exists.",
            )

    async def _ensure_slug_unique(self, slug: str) -> None:
        existing_org = await self.repository.get_by(slug=slug, deleted_at=None)
        if existing_org:
            raise ConflictError(
                error="Organization with this slug(name) already exists",
                errors={"name": "Organization with this slug(name) already exists"},
            )

    async def _ensure_domain_unique(self, domain: str) -> None:
        existing_org = await self.repository.get_by(domain=domain)
        if existing_org:
            raise ConflictError(
                error="Organization with this domain already exists",
                errors={"domain": "Organization with this domain already exists"},
            )
