from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
    DailyMotivationConfigEntity,
)
from src.modules.motivation.domain.events.motivation_domain_events import (
    DailyMotivationConfigCreatedEvent,
    DailyMotivationConfigResetEvent,
    DailyMotivationConfigUpdatedEvent,
)
from src.modules.motivation.domain.repositories.daily_motivation_config_repository import (
    IDailyMotivationConfigRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    CreateError,
    DomainError,
    InvalidError,
)


class DailyMotivationConfigDomainService:
    """
    Service class for daily motivation config domain logic.
    """

    def __init__(self, repository: IDailyMotivationConfigRepository):
        self.repository = repository

    async def create_config(
        self, config_entity: DailyMotivationConfigEntity, actor_id: int
    ) -> DailyMotivationConfigEntity:
        """
        Creates daily motivation config for an organization.
        """
        try:
            if config_entity.organization_id is None:
                raise InvalidError("Organization id is required")

            organization_id = config_entity.organization_id

            existing_config = await self.repository.get_by_organization_id(
                organization_id=organization_id
            )

            if existing_config:
                raise ConflictError(
                    error="Daily motivation config already exists for this organization"
                )

            config_entity.created_by_id = actor_id
            created_config = await self.repository.add(config_entity)

            if created_config.id is None:
                raise CreateError(error="Failed to create daily motivation config")

            created_config.add_event(
                DailyMotivationConfigCreatedEvent(
                    actor_id=actor_id,
                    organization_id=organization_id,
                    config_id=created_config.id,
                    session=self.repository.session,
                )
            )

            return created_config
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to create daily motivation config",
                internal_details=str(e),
            ) from e

    async def get_config_by_organization_id(
        self, organization_id: int
    ) -> DailyMotivationConfigEntity | None:
        """
        Retrieves daily motivation config by organization id.
        """
        return await self.repository.get_by_organization_id(
            organization_id=organization_id
        )

    async def get_or_create_default_config(
        self, organization_id: int, actor_id: int
    ) -> DailyMotivationConfigEntity:
        """
        Gets organization motivation config or creates default config if missing.
        """
        existing_config = await self.get_config_by_organization_id(
            organization_id=organization_id
        )

        if existing_config:
            return existing_config

        config_entity = DailyMotivationConfigEntity(
            organization_id=organization_id,
            sys_quote_source=True,
            is_enabled=True,
            allow_reactions=True,
            created_by_id=actor_id,
        )

        return await self.create_config(config_entity, actor_id)

    async def update_config(
        self, config_entity: DailyMotivationConfigEntity, actor_id: int
    ) -> DailyMotivationConfigEntity:
        """
        Updates daily motivation config for an organization.
        """
        try:
            if config_entity.organization_id is None:
                raise InvalidError("Organization id is required")

            organization_id = config_entity.organization_id

            existing_config = await self.repository.get_by_organization_id(
                organization_id=organization_id
            )

            if not existing_config:
                raise InvalidError("Daily motivation config not found")

            if config_entity.sys_quote_source is not None:
                existing_config.sys_quote_source = config_entity.sys_quote_source

            if config_entity.is_enabled is not None:
                existing_config.is_enabled = config_entity.is_enabled

            if config_entity.allow_reactions is not None:
                existing_config.allow_reactions = config_entity.allow_reactions

            existing_config.updated_by_id = actor_id
            existing_config.mark_updated()

            updated_config = await self.repository.update(existing_config)

            if updated_config.id is None:
                raise InvalidError("Daily motivation config not found after update")

            updated_config.add_event(
                DailyMotivationConfigUpdatedEvent(
                    actor_id=actor_id,
                    organization_id=organization_id,
                    config_id=updated_config.id,
                    session=self.repository.session,
                )
            )

            return updated_config
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to update daily motivation config",
                internal_details=str(e),
            ) from e

    async def reset_config(
        self, organization_id: int, actor_id: int
    ) -> DailyMotivationConfigEntity:
        """
        Resets daily motivation config to default values.
        """
        try:
            existing_config = await self.repository.get_by_organization_id(
                organization_id=organization_id
            )

            if not existing_config:
                return await self.get_or_create_default_config(
                    organization_id=organization_id,
                    actor_id=actor_id,
                )

            existing_config.sys_quote_source = True
            existing_config.is_enabled = True
            existing_config.allow_reactions = True
            existing_config.updated_by_id = actor_id
            existing_config.mark_updated()

            updated_config = await self.repository.update(existing_config)

            if updated_config.id is None:
                raise InvalidError("Daily motivation config not found after reset")

            updated_config.add_event(
                DailyMotivationConfigResetEvent(
                    actor_id=actor_id,
                    organization_id=organization_id,
                    config_id=updated_config.id,
                    session=self.repository.session,
                )
            )

            return updated_config
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to reset daily motivation config",
                internal_details=str(e),
            ) from e
