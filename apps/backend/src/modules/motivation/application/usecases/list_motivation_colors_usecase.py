from src.modules.motivation.domain.entities.motivation_color_entity import (
    MotivationColorEntity,
)
from src.modules.motivation.domain.services.daily_motivation_config_domain_service import (
    DailyMotivationConfigDomainService,
)
from src.modules.motivation.domain.services.motivation_color_domain_service import (
    MotivationColorDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class ListMotivationColorsUseCase:
    """
    Use case for listing motivation colors.
    """

    def __init__(
        self,
        config_domain_service: DailyMotivationConfigDomainService,
        color_domain_service: MotivationColorDomainService,
    ):
        self.config_domain_service = config_domain_service
        self.color_domain_service = color_domain_service

    async def execute(
        self,
        organization_id: int,
        actor_id: int,
    ) -> list[MotivationColorEntity]:
        """
        Execute the use case.
        """
        try:
            config = await self.config_domain_service.get_or_create_default_config(
                organization_id=organization_id,
                actor_id=actor_id,
            )

            if config.id is None:
                raise ServerError(error="Motivation config id is missing")

            return await self.color_domain_service.list_colors(
                config_id=config.id,
                actor_id=actor_id,
            )

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while listing motivation colors",
                internal_details=str(e),
            ) from e
