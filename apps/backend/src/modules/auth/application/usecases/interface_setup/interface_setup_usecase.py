from src.modules.auth.domain.services.user_onboarding_domain_service import (
    UserOnboardingDomainService,
)
from src.modules.auth.presentation.schemas.auth_interface_setup_schemas import (
    InterfaceSetupRequestSchema,
)


class InterfaceSetupUseCase:
    """
    Use case for updating the interface setup for a user.
    """

    def __init__(
        self,
        user_onboarding_domain_service: UserOnboardingDomainService,
    ):
        self.user_onboarding_domain_service = user_onboarding_domain_service

    async def execute(self, payload: InterfaceSetupRequestSchema, user_id: int):
        """
        Execute the use case to update the interface setup for a user.
        """
        language = payload.language
        _ = language

        await self.user_onboarding_domain_service.update_onboarding_theme(
            user_id=user_id, theme=payload.theme
        )
