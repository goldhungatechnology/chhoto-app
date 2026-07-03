from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.modules.visitor.domain.entities.visitor_page_visit_entity import (
    VisitorPageVisitEntity,
)
from src.modules.visitor.domain.repositories.visitor_page_visit_repository import (
    IVisitorPageVisitRepository,
)
from src.modules.visitor.infrastructure.models.visitor_page_visit_model import (
    VisitorPageVisitModel,
)
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.repository.base_repository import BaseRepository


class VisitorPageVisitRepositoryImpl(
    BaseRepository[VisitorPageVisitEntity], IVisitorPageVisitRepository
):
    """
    SQLAlchemy implementation of the visitor page-visit repository.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.table_name = VisitorPageVisitModel.__tablename__
        super().__init__(session, self.table_name)

    def to_row(self, entity: VisitorPageVisitEntity) -> dict:
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "organization_id": entity.organization_id,
            "session_id": entity.session_id,
            "visitor_id": entity.visitor_id,
            "url": entity.url,
            "page_title": entity.page_title,
            "entered_at": entity.entered_at,
            "left_at": entity.left_at,
            "duration_seconds": entity.duration_seconds,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> VisitorPageVisitEntity:
        return VisitorPageVisitEntity(
            id=row["id"],
            uuid=row["uuid"],
            organization_id=row["organization_id"],
            session_id=row["session_id"],
            visitor_id=row["visitor_id"],
            url=row["url"],
            page_title=row.get("page_title"),
            entered_at=row["entered_at"],
            left_at=row.get("left_at"),
            duration_seconds=row.get("duration_seconds"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def get_open_visit(self, session_id: int) -> VisitorPageVisitEntity | None:
        """
        Return the most-recently-entered open page visit for a session.
        """
        sql = text(
            f"SELECT * FROM {self.table_name} "
            "WHERE session_id = :session_id AND left_at IS NULL "
            "ORDER BY entered_at DESC LIMIT 1"
        )
        try:
            result = await self.session.execute(sql, {"session_id": session_id})
            row = result.mappings().one_or_none()
            return self.to_entity(dict(row)) if row else None
        except SQLAlchemyError as e:
            raise ServerError(
                error="Failed to fetch open page visit", internal_details=str(e)
            ) from e
