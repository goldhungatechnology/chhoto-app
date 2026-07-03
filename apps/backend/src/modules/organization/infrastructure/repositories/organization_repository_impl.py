from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.modules.organization.domain.entities.organization_entity import (
    OrganizationEntity,
)
from src.modules.organization.domain.repositories.organization_repository import (
    IOrganizationRepository,
)
from src.modules.organization.infrastructure.models.organization_member_model import (
    OrganizationMemberModel,
)
from src.modules.organization.infrastructure.models.organization_model import (
    OrganizationModel,
)

from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.repository.base_repository import BaseRepository


class OrganizationRepositoryImpl(
    BaseRepository[OrganizationEntity], IOrganizationRepository
):
    """
    SQLAlchemy implementation of the organization repository.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.table_name = OrganizationModel.__tablename__
        super().__init__(session, self.table_name)

    def to_row(self, entity: OrganizationEntity) -> dict:
        """
        Convert an OrganizationEntity to a dictionary representing a database row.
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "name": entity.name,
            "description": entity.description,
            "type": entity.type,
            "slug": entity.slug,
            "logo": entity.logo,
            "domain": entity.domain,
            "status": entity.status,
            "owner_id": entity.owner_id,
            "created_by_id": entity.created_by_id,
            "updated_by_id": entity.updated_by_id,
            "deleted_at": entity.deleted_at,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> OrganizationEntity:
        """
        Convert a database row dictionary to an OrganizationEntity.
        """
        return OrganizationEntity(
            id=row["id"],
            uuid=row["uuid"],
            name=row["name"],
            description=row.get("description"),
            type=row["type"],
            slug=row["slug"],
            logo=row.get("logo"),
            domain=row["domain"],
            status=row["status"],
            owner_id=row["owner_id"],
            created_by_id=row.get("created_by_id"),
            updated_by_id=row.get("updated_by_id"),
            deleted_at=row.get("deleted_at"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def list_by_user_id(self, user_id: int) -> list[OrganizationEntity] | None:
        """
        list all oragnizations by user _id
        """
        # Safety check: if table is not migrated, return empty list to prevent transaction abort.
        try:
            check_sql = text("SELECT to_regclass('org_organizations')")
            check_res = await self.session.execute(check_sql)
            if check_res.scalar() is None:
                return []
        except Exception:
            return []

        sql = text(
            f"SELECT o.* FROM {self.table_name} o "
            f"JOIN {OrganizationMemberModel.__tablename__} om ON o.id = om.organization_id "
            f"WHERE om.user_id = :user_id AND o.deleted_at IS NULL"
        )

        try:
            result = await self.session.execute(sql, {"user_id": user_id})
            rows = result.mappings().all()
            return [self.to_entity(dict(row)) for row in rows]
        except SQLAlchemyError as e:
            raise ServerError(
                "Failed to list organizations by user ID", internal_details=str(e)
            ) from e

