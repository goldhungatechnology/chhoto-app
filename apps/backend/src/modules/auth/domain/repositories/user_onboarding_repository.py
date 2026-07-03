from src.modules.auth.domain.entities.user_onboarding_entity import UserOnboardingEntity
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IUserOnboardingRepository(IBaseRepository[UserOnboardingEntity]):
    """
    Interface for the User onboarding repository.
    """
