from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.workforce.domain.entities.rbac.rbac_role_entity import RoleEntity
from src.modules.workforce.domain.repositories.rbac.rbac_role_repository import (
    IRoleRepository,
)
from src.modules.workforce.infrastructure.models.rbac.rbac_role_model import RoleModel
from src.shared.infrastructure.repository.organization_repository import (
    OrganizationRepository,
)


class RoleRepositoryImpl(OrganizationRepository[RoleEntity], IRoleRepository):
    """
    sqlalchemy implementation of the role repository interface
    """

    def __init__(self, session: AsyncSession, organization_id: int):
        """Initialize RoleRepositoryImpl with an async database session."""
        self.session = session
        self.organization_id = organization_id
        self.table_name = RoleModel.__tablename__

        super().__init__(
            session=session, table_name=self.table_name, organization_id=organization_id
        )

    def to_row(self, entity: RoleEntity) -> dict:
        """
        convert a role entity to a role model
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "name": entity.name,
            "description": entity.description,
            "is_system_role": entity.is_system_role,
            "created_by_id": entity.created_by_id,
            "updated_by_id": entity.updated_by_id,
            "deleted_at": entity.deleted_at,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "organization_id": entity.organization_id,
        }

    def to_entity(self, row: dict) -> RoleEntity:
        """
        convert a role model to a role entity
        """
        return RoleEntity(
            id=row["id"],
            uuid=row["uuid"],
            name=row["name"],
            description=row["description"],
            is_system_role=row["is_system_role"],
            created_by_id=row.get("created_by_id"),
            updated_by_id=row.get("updated_by_id"),
            deleted_at=row.get("deleted_at"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            organization_id=row["organization_id"],
        )
