from src.modules.auth.domain.entities.user_onboarding_entity import UserOnboardingEntity
from src.modules.auth.domain.events.auth_onboarding_domain_events import (
    UserOnboardingCompletedEvent,
)
from src.modules.auth.domain.repositories.user_onboarding_repository import (
    IUserOnboardingRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    CreateError,
    DomainError,
    UpdateError,
)


class UserOnboardingDomainService:
    """
    This class is responsible for handling the user onboarding process
    """

    def __init__(self, repository: IUserOnboardingRepository):
        self.repository = repository

    async def create_user_onboarding(self, onboarding_entity):
        """
        Creates a new user onboarding record in the database.
        """
        try:
            existing_onboarding = await self.repository.get_by(
                user_id=onboarding_entity.user_id
            )
            if existing_onboarding:
                raise ConflictError(
                    "User onboarding already exists for this user",
                )
            created_onboarding = await self.repository.add(onboarding_entity)

            created_onboarding.add_event(
                UserOnboardingCompletedEvent(
                    user_id=created_onboarding.user_id,
                    theme=created_onboarding.theme,
                    referral_source=created_onboarding.referral_source,
                )
            )

            return created_onboarding
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                "Failed to create user onboarding", internal_details=str(e)
            ) from e

    async def get_user_onboarding_by_user_id(self, user_id: int):
        """
        Retrieves a user onboarding record by user ID.
        """
        try:
            onboarding = await self.repository.get_by(user_id=user_id)
            if not onboarding:
                return None
            return onboarding
        except DomainError:
            raise
        except Exception as e:
            raise DomainError(
                "Failed to retrieve user onboarding", internal_details=str(e)
            ) from e

    async def update_onboarding_theme(
        self, user_id: int, theme: str
    ) -> UserOnboardingEntity:
        """
        update onboarding theme
        """
        try:
            onboarding = await self.repository.get_by(user_id=user_id)
            if not onboarding:
                raise DomainError("User onboarding not found for this user")
            onboarding.theme = theme
            onboarding.mark_updated()
            return await self.repository.update(onboarding)
        except DomainError:
            raise
        except Exception as e:
            raise UpdateError(
                "Failed to update user onboarding theme", internal_details=str(e)
            ) from e
