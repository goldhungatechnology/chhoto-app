from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from src.modules.workforce.domain.entities.rbac.rbac_permission_entity import (
    PermissionEntity,
)
from src.modules.workforce.domain.repositories.rbac.rbac_permission_repository import (
    IPermissionRepository,
)
from src.modules.workforce.infrastructure.models.rbac.rbac_permission_model import (
    PermissionModel,
)
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.repository.organization_repository import (
    OrganizationRepository,
)


class PermissionRepositoryImpl(
    OrganizationRepository[PermissionEntity], IPermissionRepository
):
    """
    sqlalchemy implementation of the permission repository interface
    """

    def __init__(self, session: AsyncSession, organization_id: int):
        """Initialize PermissionRepositoryImpl with an async database session."""
        self.session = session
        self.organization_id = organization_id
        self.table_name = PermissionModel.__tablename__

        super().__init__(
            session=session, table_name=self.table_name, organization_id=organization_id
        )

    def to_row(self, entity: PermissionEntity) -> dict:
        """
        convert a permission entity to a permission model
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "name": entity.name,
            "key": entity.key,
            "description": entity.description,
            "category": entity.category,
            "is_system_permission": entity.is_system_permission,
            "organization_id": entity.organization_id,
            "created_by_id": entity.created_by_id,
            "updated_by_id": entity.updated_by_id,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> PermissionEntity:
        """
        convert a permission model to a permission entity
        """
        return PermissionEntity(
            id=row["id"],
            uuid=row["uuid"],
            name=row["name"],
            key=row["key"],
            description=row["description"],
            category=row["category"],
            is_system_permission=row["is_system_permission"],
            organization_id=row.get("organization_id"),
            created_by_id=row.get("created_by_id"),
            updated_by_id=row.get("updated_by_id"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def list_permissions_by_organization_id(self) -> list[PermissionEntity]:
        """
        Lists all permissions for the organization.
        """
        sql = text(
            f"SELECT * FROM {self.table_name} WHERE organization_id = :organization_id OR organization_id IS NULL"
        )

        try:
            result = await self.session.execute(
                sql, {"organization_id": self.organization_id}
            )
            rows = result.mappings().all()
            return [self.to_entity(dict(row)) for row in rows]
        except Exception as e:
            raise ServerError(
                error="Failed to list permissions", internal_details=str(e)
            ) from e
