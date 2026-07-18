from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.links.domain.entities.link_entity import LinkEntity
from src.modules.links.domain.repositories.link_repository import ILinkRepository
from src.modules.links.infrastructure.models.link_model import LinkModel
from src.shared.infrastructure.repository.base_repository import BaseRepository


class LinkRepositoryImpl(BaseRepository[LinkEntity], ILinkRepository):
    """
    SQLAlchemy implementation of the link repository interface.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.table_name = LinkModel.__tablename__
        super().__init__(session, self.table_name)

    def to_row(self, entity: LinkEntity) -> dict:
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "user_id": entity.user_id,
            "destination_url": entity.destination_url,
            "short_url": entity.short_url,
            "tags": entity.tags,
            "auto_expire": entity.auto_expire,
            "total_clicks": entity.total_clicks,
            "title": entity.title,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> LinkEntity:
        return LinkEntity(
            id=row["id"],
            uuid=row["uuid"],
            user_id=row["user_id"],
            destination_url=row["destination_url"],
            short_url=row["short_url"],
            tags=row.get("tags"),
            auto_expire=row.get("auto_expire"),
            total_clicks=row.get("total_clicks", 0),
            title=row.get("title"),
            created_at=row["created_at"],
            updated_at=row.get("updated_at"),
        )
