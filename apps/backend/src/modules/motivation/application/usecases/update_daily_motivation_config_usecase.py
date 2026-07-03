from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
    DailyMotivationConfigEntity,
)
from src.modules.motivation.domain.services.daily_motivation_config_domain_service import (
    DailyMotivationConfigDomainService,
)
from src.modules.motivation.presentation.schemas.motivation_schemas import (
    UpdateDailyMotivationConfigRequestSchema,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class UpdateDailyMotivationConfigUseCase:
    """
    Use case for updating daily motivation config.
    """

    def __init__(
        self,
        daily_motivation_config_domain_service: DailyMotivationConfigDomainService,
    ):
        self.daily_motivation_config_domain_service = (
            daily_motivation_config_domain_service
        )

    async def execute(
        self,
        payload: UpdateDailyMotivationConfigRequestSchema,
        organization_id: int,
        actor_id: int,
    ) -> DailyMotivationConfigEntity:
        """
        Execute the use case.
        """
        try:
            config_entity = DailyMotivationConfigEntity(
                organization_id=organization_id,
                sys_quote_source=payload.sys_quote_source,
                is_enabled=payload.is_enabled,
                allow_reactions=payload.allow_reactions,
                updated_by_id=actor_id,
            )

            return await self.daily_motivation_config_domain_service.update_config(
                config_entity=config_entity,
                actor_id=actor_id,
            )
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while updating daily motivation config",
                internal_details=str(e),
            ) from e
