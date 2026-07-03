from src.modules.auth.domain.entities.user_onboarding_entity import UserOnboardingEntity
from src.modules.auth.domain.services.user_domain_service import UserDomainService
from src.modules.auth.domain.services.user_onboarding_domain_service import (
    UserOnboardingDomainService,
)
from src.modules.auth.presentation.schemas.auth_onboarding_schemas import (
    OnboardingRequestSchema,
)
from src.shared.mediator.mediator import mediator


class CreateOnboardingUseCase:
    """
    Use case for creating an onboarding process for a user.
    """

    def __init__(
        self,
        user_onboarding_domain_service: UserOnboardingDomainService,
        user_domain_service: UserDomainService,
    ):
        self.user_onboarding_domain_service = user_onboarding_domain_service
        self.user_domain_service = user_domain_service

    async def execute(self, payload: OnboardingRequestSchema, user_id: int):
        """
        Executes the use case to create a new onboarding process for a user.

        1. Creates a new onboarding record for the user with the provided theme and referral source.
        2. Marks the user as onboarded within the same transaction.
        3. Publishes events after successful creation.
        """
        onboarding = UserOnboardingEntity(
            user_id=user_id,
            theme=payload.theme,
            referral_source=payload.referral_source,
        )
        created_onboarding = (
            await self.user_onboarding_domain_service.create_user_onboarding(onboarding)
        )

        updated_user = await self.user_domain_service.mark_onboarded(
            user_id=user_id
        )

        for event in created_onboarding.pull_events():
            await mediator.publish(event)
        for event in updated_user.pull_events():
            await mediator.publish(event)

        return created_onboarding
