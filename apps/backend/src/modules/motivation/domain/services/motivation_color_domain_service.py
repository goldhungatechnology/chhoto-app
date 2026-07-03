from src.modules.motivation.domain.entities.motivation_color_entity import (
    MotivationColorEntity,
)
from src.modules.motivation.domain.repositories.motivation_color_repository import (
    IMotivationColorRepository,
)
from src.shared.exceptions.base_exceptions import (
    CreateError,
    DomainError,
    InvalidError,
)


class MotivationColorDomainService:
    """
    Service class for motivation color domain logic.

    This service manages the 5-color queue for a motivation config.

    Queue behavior:
    A B C D E + G = B C D E G

    POST returns only newly created color.
    GET list will return colors from newest to oldest.
    """

    MAX_COLORS = 5

    DEFAULT_COLORS = [
        "#7C3AED",
        "#F59E0B",
        "#059669",
        "#2563EB",
        "#7E22CE",
    ]

    def __init__(self, repository: IMotivationColorRepository):
        self.repository = repository

    async def list_colors(
        self,
        config_id: int,
        actor_id: int,
    ) -> list[MotivationColorEntity]:
        """
        Lists motivation colors for a motivation config.

        Returns newest color first.
        """
        try:
            colors = await self.repository.list_by_config_id(
                config_id=config_id,
            )

            return list(reversed(colors))

        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to list motivation colors",
                internal_details=str(e),
            ) from e

    async def add_color(
        self,
        config_id: int,
        color_code: str,
        actor_id: int,
    ) -> MotivationColorEntity:
        """
        Adds a new motivation color using queue behavior.

        If color already exists, it is moved to the latest position.
        If there are already 5 colors, the oldest color is removed.

        Returns only the newly created color.
        """
        try:
            color_code = self._validate_color_code(color_code)

            existing_colors = await self.repository.list_by_config_id(
                config_id=config_id,
            )

            while len(existing_colors) >= self.MAX_COLORS:
                oldest_color = existing_colors[0]

                if oldest_color.id is None:
                    raise InvalidError("Oldest motivation color id is missing")

                await self.repository.delete_by_id(oldest_color.id)
                existing_colors.pop(0)

            color_entity = MotivationColorEntity(
                config_id=config_id,
                color_code=color_code,
                created_by_id=actor_id,
                updated_by_id=actor_id,
            )

            created_color = await self.repository.add(color_entity)

            if created_color.id is None:
                raise CreateError(error="Failed to create motivation color")

            return created_color

        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to add motivation color",
                internal_details=str(e),
            ) from e

    def _validate_color_code(
        self,
        color_code: str,
    ) -> str:
        """
        Validates motivation color code.
        """
        color_code = color_code.strip()

        if not color_code:
            raise InvalidError("Color code is required")

        return color_code
