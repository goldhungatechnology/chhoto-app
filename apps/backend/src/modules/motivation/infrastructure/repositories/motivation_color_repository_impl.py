from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.motivation.domain.entities.motivation_color_entity import (
    MotivationColorEntity,
)
from src.modules.motivation.domain.repositories.motivation_color_repository import (
    IMotivationColorRepository,
)
from src.modules.motivation.infrastructure.models.motivation_color_model import (
    MotivationColorModel,
)
from src.shared.infrastructure.repository.base_repository import BaseRepository


class MotivationColorRepositoryImpl(
    BaseRepository[MotivationColorEntity],
    IMotivationColorRepository,
):
    """
    Repository implementation for motivation colors.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.table_name = MotivationColorModel.__tablename__
        super().__init__(session, self.table_name)

    def to_row(self, entity: MotivationColorEntity) -> dict:
        """
        Convert MotivationColorEntity to database row.
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "config_id": entity.config_id,
            "color_code": entity.color_code,
            "created_by_id": entity.created_by_id,
            "updated_by_id": entity.updated_by_id,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> MotivationColorEntity:
        """
        Convert database row to MotivationColorEntity.
        """
        return MotivationColorEntity(
            id=row["id"],
            uuid=row["uuid"],
            config_id=row["config_id"],
            color_code=row["color_code"],
            created_by_id=row.get("created_by_id"),
            updated_by_id=row.get("updated_by_id"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def list_by_config_id(
        self,
        config_id: int,
    ) -> list[MotivationColorEntity]:
        """
        List motivation colors by config id in queue order.
        """
        stmt = (
            select(MotivationColorModel)
            .where(MotivationColorModel.config_id == config_id)
            .order_by(
                MotivationColorModel.created_at.asc(),
                MotivationColorModel.id.asc(),
            )
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [
            MotivationColorEntity(
                id=model.id,
                uuid=str(model.uuid),
                config_id=model.config_id,
                color_code=model.color_code,
                created_at=model.created_at,
                updated_at=model.updated_at,
                created_by_id=model.created_by_id,
                updated_by_id=model.updated_by_id,
            )
            for model in models
        ]

    async def delete_by_id(
        self,
        color_id: int,
    ) -> None:
        """
        Delete motivation color by id.
        """
        stmt = delete(MotivationColorModel).where(MotivationColorModel.id == color_id)

        await self.session.execute(stmt)
        await self.session.flush()
