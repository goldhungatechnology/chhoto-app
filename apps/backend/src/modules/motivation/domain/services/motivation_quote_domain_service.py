from datetime import UTC, datetime

from src.modules.motivation.domain.entities.motivation_quote_entity import (
    MotivationQuoteEntity,
)
from src.modules.motivation.domain.enums.motivation_enums import QuotesStatusEnum
from src.modules.motivation.domain.events.motivation_domain_events import (
    CustomMotivationQuoteCreatedEvent,
    CustomMotivationQuoteDeletedEvent,
    CustomMotivationQuoteStatusChangedEvent,
    CustomMotivationQuoteUpdatedEvent,
)
from src.modules.motivation.domain.repositories.daily_motivation_config_repository import (
    IDailyMotivationConfigRepository,
)
from src.modules.motivation.domain.repositories.motivation_quote_repository import (
    IMotivationQuoteRepository,
)
from src.shared.exceptions.base_exceptions import CreateError, DomainError, InvalidError


class MotivationQuoteDomainService:
    """
    Service class for motivation quote domain logic.
    """

    def __init__(
        self,
        quote_repository: IMotivationQuoteRepository,
        config_repository: IDailyMotivationConfigRepository,
    ):
        self.quote_repository = quote_repository
        self.config_repository = config_repository

    async def create_custom_quote(
        self,
        quote_entity: MotivationQuoteEntity,
        actor_id: int,
    ) -> MotivationQuoteEntity:
        """
        Creates a custom motivation quote for an organization.
        """
        try:
            organization_id = self._get_required_organization_id(quote_entity)

            self._validate_quote_text(quote_entity.context)
            self._validate_status(quote_entity.status)

            quote_entity.is_sys_default = False
            quote_entity.created_by_id = actor_id

            created_quote = await self.quote_repository.add(quote_entity)

            if not created_quote.id:
                raise CreateError(error="Failed to create custom motivation quote")

            created_quote.add_event(
                CustomMotivationQuoteCreatedEvent(
                    actor_id=actor_id,
                    organization_id=organization_id,
                    quote_uuid=created_quote.uuid,
                    session=self.quote_repository.session,
                )
            )

            return created_quote

        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to create custom motivation quote",
                internal_details=str(e),
            ) from e

    async def list_custom_quotes(
        self,
        organization_id: int,
        status: str | None = None,
        search: str | None = None,
    ) -> list[MotivationQuoteEntity]:
        """
        Lists custom motivation quotes of an organization.
        """
        if status:
            self._validate_status(status)

        return await self.quote_repository.list_by_organization_id(
            organization_id=organization_id,
            is_sys_default=False,
            status=status,
            search=search,
        )

    async def get_quote_by_uuid(
        self,
        quote_uuid: str,
        organization_id: int,
    ) -> MotivationQuoteEntity:
        """
        Retrieves one custom motivation quote by UUID and organization id.
        """
        quote = await self.quote_repository.get_by(
            uuid=quote_uuid,
            organization_id=organization_id,
            deleted_at=None,
        )

        if not quote:
            raise InvalidError("Motivation quote not found")

        if quote.is_sys_default:
            raise InvalidError(
                "System default quote cannot be retrieved from custom quote flow"
            )

        return quote

    async def update_custom_quote(
        self,
        quote_entity: MotivationQuoteEntity,
        actor_id: int,
    ) -> MotivationQuoteEntity:
        """
        Updates an existing custom motivation quote.
        """
        try:
            if not quote_entity.uuid:
                raise InvalidError("Quote uuid is required")

            organization_id = self._get_required_organization_id(quote_entity)

            existing_quote = await self.quote_repository.get_by(
                uuid=quote_entity.uuid,
                organization_id=organization_id,
                deleted_at=None,
            )

            if not existing_quote:
                raise InvalidError("Motivation quote not found")

            if existing_quote.is_sys_default:
                raise InvalidError(
                    "System default quote cannot be updated from custom quote flow"
                )

            if quote_entity.context is not None:
                self._validate_quote_text(quote_entity.context)
                existing_quote.context = quote_entity.context

            if quote_entity.author_name is not None:
                existing_quote.author_name = quote_entity.author_name

            if quote_entity.status is not None:
                self._validate_status(quote_entity.status)
                existing_quote.status = quote_entity.status

            if quote_entity.font_style is not None:
                existing_quote.font_style = quote_entity.font_style

            if quote_entity.theme_color is not None:
                existing_quote.theme_color = quote_entity.theme_color

            if quote_entity.bg_image is not None:
                existing_quote.bg_image = quote_entity.bg_image

            existing_quote.updated_by_id = actor_id
            existing_quote.mark_updated()

            updated_quote = await self.quote_repository.update(existing_quote)

            if not updated_quote.uuid:
                raise InvalidError("Motivation quote not found after update")

            updated_quote.add_event(
                CustomMotivationQuoteUpdatedEvent(
                    actor_id=actor_id,
                    organization_id=organization_id,
                    quote_uuid=updated_quote.uuid,
                    session=self.quote_repository.session,
                )
            )

            return updated_quote

        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to update custom motivation quote",
                internal_details=str(e),
            ) from e

    async def delete_custom_quote(
        self,
        organization_id: int,
        quote_uuid: str,
        actor_id: int,
    ) -> MotivationQuoteEntity:
        """
        Soft deletes a custom motivation quote.
        """
        try:
            existing_quote = await self.quote_repository.get_by(
                uuid=quote_uuid,
                organization_id=organization_id,
                deleted_at=None,
            )

            if not existing_quote:
                raise InvalidError("Motivation quote not found")

            if existing_quote.is_sys_default:
                raise InvalidError("System default quote cannot be deleted.")

            existing_quote.deleted_at = datetime.now(UTC)
            existing_quote.updated_by_id = actor_id
            existing_quote.mark_updated()

            deleted_quote = await self.quote_repository.update(existing_quote)

            if not deleted_quote.uuid:
                raise InvalidError("Motivation quote not found after delete")

            deleted_quote.add_event(
                CustomMotivationQuoteDeletedEvent(
                    actor_id=actor_id,
                    organization_id=organization_id,
                    quote_uuid=deleted_quote.uuid,
                    session=self.quote_repository.session,
                )
            )

            return deleted_quote

        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to delete custom motivation quote",
                internal_details=str(e),
            ) from e

    async def change_custom_quote_status(
        self,
        organization_id: int,
        quote_uuid: str,
        status: str,
        actor_id: int,
    ) -> MotivationQuoteEntity:
        """
        Changes status of a custom motivation quote.
        """
        try:
            self._validate_status(status)

            existing_quote = await self.quote_repository.get_by(
                uuid=quote_uuid,
                organization_id=organization_id,
                deleted_at=None,
            )

            if not existing_quote:
                raise InvalidError("Motivation quote not found")

            if existing_quote.is_sys_default:
                raise InvalidError(
                    "System default quote status cannot be changed from custom quote flow"
                )

            if existing_quote.status is None:
                raise InvalidError("Quote status cannot be None")

            old_status: str = existing_quote.status

            existing_quote.status = status
            existing_quote.updated_by_id = actor_id
            existing_quote.mark_updated()

            updated_quote = await self.quote_repository.update(existing_quote)

            if not updated_quote.uuid:
                raise InvalidError("Motivation quote not found after status update")

            updated_quote.add_event(
                CustomMotivationQuoteStatusChangedEvent(
                    actor_id=actor_id,
                    organization_id=organization_id,
                    quote_uuid=updated_quote.uuid,
                    old_status=old_status,
                    new_status=status,
                    session=self.quote_repository.session,
                )
            )

            return updated_quote

        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to change custom motivation quote status",
                internal_details=str(e),
            ) from e

    async def get_daily_quote(
        self,
        organization_id: int,
    ) -> MotivationQuoteEntity | None:
        """
        Selects quote to show today.
        """
        config = await self.config_repository.get_by_organization_id(
            organization_id=organization_id
        )

        if config and not config.is_enabled:
            return None

        if config and config.sys_quote_source:
            return await self.quote_repository.get_active_system_quote()

        custom_quote = await self.quote_repository.get_active_custom_quote(
            organization_id=organization_id
        )

        if custom_quote:
            return custom_quote

        return await self.quote_repository.get_active_system_quote()

    async def get_preview_slider_quotes(
        self,
        organization_id: int,
        limit: int = 3,
    ) -> list[MotivationQuoteEntity]:
        """
        Get motivation quotes for preview/slider.

        Logic:
        1. Return active custom quote first.
        2.If custom quotes are less than 3, fill remaining slides with system quotes.
        3. If no custom quotes exist, return up to 3 active system quotes.
        4. If both custom and system quotes exist, custom quotes are prioritized.
        """
        if not organization_id:
            raise InvalidError("Organization id is required for preview slider quotes")

        custom_quotes = (
            await self.quote_repository.list_active_custom_quotes_for_preview(
                organization_id=organization_id,
                limit=limit,
            )
        )

        if len(custom_quotes) >= limit:
            return custom_quotes[:limit]

        remaining_limit = limit - len(custom_quotes)

        system_quotes = (
            await self.quote_repository.list_active_system_quotes_for_preview(
                limit=remaining_limit,
            )
        )

        return custom_quotes + system_quotes

    def _validate_quote_text(self, text: str | None) -> None:
        """
        Validate quote text.
        """
        if not text or not text.strip():
            raise InvalidError("Motivation quote text is required")

    def _validate_status(self, status: str | None) -> None:
        """
        Validate quote status using enum.
        """
        if status is None:
            raise InvalidError("Quote status is required")

        try:
            QuotesStatusEnum(status)
        except ValueError as e:
            raise InvalidError("Invalid motivation quote status") from e

    def _get_required_organization_id(
        self,
        quote_entity: MotivationQuoteEntity,
    ) -> int:
        """
        Get organization id for custom quote flows.
        """
        if quote_entity.organization_id is None:
            raise InvalidError(
                "Organization id is required for custom motivation quote"
            )

        return quote_entity.organization_id

    async def list_system_quotes(
        self,
        organization_id: int,
        status: str | None = None,
        search: str | None = None,
    ) -> list[MotivationQuoteEntity]:
        """
        List global system/sample motivation quotes.
        """
        if status:
            self._validate_status(status)

        return await self.quote_repository.list_system_quotes(
            organization_id=organization_id,
            status=status,
            search=search,
        )

    async def get_system_quote_detail(
        self,
        quote_uuid: str,
    ) -> MotivationQuoteEntity:
        """
        Get global system/sample motivation quote detail.
        """
        quote = await self.quote_repository.get_system_quote_by_uuid(
            quote_uuid=quote_uuid,
        )

        if not quote:
            raise InvalidError("System motivation quote not found")

        return quote
