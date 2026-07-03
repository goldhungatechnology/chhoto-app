from src.modules.organization.domain.entities.organization_onboarding_entity import (
    OrganizationOnboardingEntity,
)
from src.modules.organization.domain.repositories.organization_onboarding_repository import (
    IOrganizationOnboardingRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    CreateError,
    DomainError,
)


class OrganizationOnboardingDomainService:
    """
    service class for organization onboarding domain logic
    """

    def __init__(self, repository: IOrganizationOnboardingRepository):
        self.repository = repository

    async def create_organization_onboarding(
        self, onboarding_entity: OrganizationOnboardingEntity
    ):
        """
        Creates a new organization onboarding record in the database.
        """
        try:
            existing_onboarding = await self.repository.get_by(
                organization_id=onboarding_entity.organization_id
            )
            if existing_onboarding:
                raise ConflictError(
                    "Organization onboarding already exists for this organization",
                )
            created_onboarding = await self.repository.add(onboarding_entity)

            return created_onboarding
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                "Failed to create organization onboarding", internal_details=str(e)
            ) from e
