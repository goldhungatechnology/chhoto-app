from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.visitor.domain.entities.visitor_entity import VisitorEntity
from src.modules.visitor.domain.repositories.visitor_repository import (
    IVisitorRepository,
)
from src.modules.visitor.infrastructure.models.visitor_model import VisitorModel
from src.shared.infrastructure.repository.base_repository import BaseRepository


class VisitorRepositoryImpl(BaseRepository[VisitorEntity], IVisitorRepository):
    """
    SQLAlchemy implementation of the visitor repository.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.table_name = VisitorModel.__tablename__
        super().__init__(session, self.table_name)

    def to_row(self, entity: VisitorEntity) -> dict:
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "organization_id": entity.organization_id,
            "external_id": entity.external_id,
            "last_seen_at": entity.last_seen_at,
            "visit_count": entity.visit_count,
            "is_identified": entity.is_identified,
            "name": entity.name,
            "email": entity.email,
            "phone": entity.phone,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> VisitorEntity:
        return VisitorEntity(
            id=row["id"],
            uuid=row["uuid"],
            organization_id=row["organization_id"],
            external_id=row["external_id"],
            last_seen_at=row["last_seen_at"],
            visit_count=row["visit_count"],
            is_identified=row["is_identified"],
            name=row.get("name"),
            email=row.get("email"),
            phone=row.get("phone"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def get_by_external_id(
        self, organization_id: int, external_id: str
    ) -> VisitorEntity | None:
        """
        Fetch a visitor by its organization-scoped external id.
        """
        return await self.get_by(
            organization_id=organization_id, external_id=external_id
        )
