from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.links.domain.entities.link_session_entity import LinkSessionEntity
from src.modules.links.domain.repositories.link_session_repository import (
    ILinkSessionRepository,
)
from src.modules.links.infrastructure.models.link_session_model import LinkSessionModel
from src.shared.infrastructure.repository.base_repository import BaseRepository


class LinkSessionRepositoryImpl(
    BaseRepository[LinkSessionEntity], ILinkSessionRepository
):
    """
    SQLAlchemy implementation of the link session repository interface.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.table_name = LinkSessionModel.__tablename__
        super().__init__(session, self.table_name)

    def to_row(self, entity: LinkSessionEntity) -> dict:
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "link_id": entity.link_id,
            "ip_address": entity.ip_address,
            "device": entity.device,
            "browser": entity.browser,
            "referral_source": entity.referral_source,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> LinkSessionEntity:
        return LinkSessionEntity(
            id=row["id"],
            uuid=row["uuid"],
            link_id=row["link_id"],
            ip_address=row.get("ip_address"),
            device=row.get("device"),
            browser=row.get("browser"),
            referral_source=row.get("referral_source"),
            created_at=row["created_at"],
            updated_at=row.get("updated_at"),
        )
