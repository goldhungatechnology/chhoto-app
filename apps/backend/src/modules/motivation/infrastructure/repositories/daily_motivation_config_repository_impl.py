from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
    DailyMotivationConfigEntity,
)
from src.modules.motivation.domain.repositories.daily_motivation_config_repository import (
    IDailyMotivationConfigRepository,
)
from src.modules.motivation.infrastructure.models.daily_motivation_config_model import (
    DailyMotivationConfigModel,
)
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.repository.base_repository import BaseRepository


class DailyMotivationConfigRepositoryImpl(
    BaseRepository[DailyMotivationConfigEntity], IDailyMotivationConfigRepository
):
    """
    SQLAlchemy implementation of the daily motivation config repository.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.table_name = DailyMotivationConfigModel.__tablename__
        super().__init__(session, self.table_name)

    def to_row(self, entity: DailyMotivationConfigEntity) -> dict:
        """
        Convert DailyMotivationConfigEntity to database row.
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "organization_id": entity.organization_id,
            "sys_quote_source": entity.sys_quote_source,
            "is_enabled": entity.is_enabled,
            "allow_reactions": entity.allow_reactions,
            "created_by_id": entity.created_by_id,
            "updated_by_id": entity.updated_by_id,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> DailyMotivationConfigEntity:
        """
        Convert database row to DailyMotivationConfigEntity.
        """
        return DailyMotivationConfigEntity(
            id=row["id"],
            uuid=row["uuid"],
            organization_id=row["organization_id"],
            sys_quote_source=row["sys_quote_source"],
            is_enabled=row["is_enabled"],
            allow_reactions=row["allow_reactions"],
            created_by_id=row.get("created_by_id"),
            updated_by_id=row.get("updated_by_id"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def get_by_organization_id(
        self, organization_id: int
    ) -> DailyMotivationConfigEntity | None:
        """
        Get motivation config by organization id.
        """
        try:
            return await self.get_by(organization_id=organization_id)
        except SQLAlchemyError as e:
            raise ServerError(
                "Failed to get daily motivation config by organization id",
                internal_details=str(e),
            ) from e
