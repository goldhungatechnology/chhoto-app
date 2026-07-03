from src.modules.organization.domain.entities.organization_onboarding_entity import (
    OrganizationOnboardingEntity,
)
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IOrganizationOnboardingRepository(IBaseRepository[OrganizationOnboardingEntity]):
    """
    Interface for the organization member repository.
    """
