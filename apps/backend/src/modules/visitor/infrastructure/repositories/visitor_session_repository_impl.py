from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.visitor.domain.entities.visitor_session_entity import (
    VisitorSessionEntity,
)
from src.modules.visitor.domain.repositories.visitor_session_repository import (
    IVisitorSessionRepository,
)
from src.modules.visitor.infrastructure.models.visitor_session_model import (
    VisitorSessionModel,
)
from src.shared.infrastructure.repository.base_repository import BaseRepository


class VisitorSessionRepositoryImpl(
    BaseRepository[VisitorSessionEntity], IVisitorSessionRepository
):
    """
    SQLAlchemy implementation of the visitor session repository.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.table_name = VisitorSessionModel.__tablename__
        super().__init__(session, self.table_name)

    def to_row(self, entity: VisitorSessionEntity) -> dict:
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "organization_id": entity.organization_id,
            "visitor_id": entity.visitor_id,
            "status": entity.status,
            "started_at": entity.started_at,
            "ended_at": entity.ended_at,
            "ip_address": entity.ip_address,
            "user_agent": entity.user_agent,
            "referer": entity.referer,
            "landing_page": entity.landing_page,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> VisitorSessionEntity:
        return VisitorSessionEntity(
            id=row["id"],
            uuid=row["uuid"],
            organization_id=row["organization_id"],
            visitor_id=row["visitor_id"],
            status=row["status"],
            started_at=row["started_at"],
            ended_at=row.get("ended_at"),
            ip_address=row.get("ip_address"),
            user_agent=row.get("user_agent"),
            referer=row.get("referer"),
            landing_page=row.get("landing_page"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
