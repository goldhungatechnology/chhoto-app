from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
    DailyMotivationConfigEntity,
)
from src.modules.motivation.domain.services.daily_motivation_config_domain_service import (
    DailyMotivationConfigDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class ResetDailyMotivationConfigUseCase:
    """
    Use case for resetting daily motivation config.
    """

    def __init__(
        self,
        daily_motivation_config_domain_service: DailyMotivationConfigDomainService,
    ):
        self.daily_motivation_config_domain_service = (
            daily_motivation_config_domain_service
        )

    async def execute(
        self, organization_id: int, actor_id: int
    ) -> DailyMotivationConfigEntity:
        """
        Execute the use case.
        """
        try:
            return await self.daily_motivation_config_domain_service.reset_config(
                organization_id=organization_id,
                actor_id=actor_id,
            )
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while resetting daily motivation config",
                internal_details=str(e),
            ) from e
