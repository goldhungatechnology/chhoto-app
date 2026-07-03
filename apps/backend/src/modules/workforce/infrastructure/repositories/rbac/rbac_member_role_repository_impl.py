from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.workforce.domain.entities.rbac.rbac_member_role_entity import (
    MemberRoleEntity,
)
from src.modules.workforce.domain.repositories.rbac.rbac_member_role_repository import (
    IMemberRoleRepository,
)
from src.modules.workforce.infrastructure.models.rbac.rbac_member_role_model import (
    MemberRoleModel,
)
from src.shared.infrastructure.repository.base_repository import BaseRepository


class MemberRoleRepositoryImpl(BaseRepository[MemberRoleEntity], IMemberRoleRepository):
    """
    sqlalchemy implementation of the member role repository interface
    """

    def __init__(self, session: AsyncSession):
        """Initialize MemberRoleRepositoryImpl with an async database session."""
        self.session = session
        self.table_name = MemberRoleModel.__tablename__

        super().__init__(session=session, table_name=self.table_name)

    def to_row(self, entity: MemberRoleEntity) -> dict:
        """
        convert a member role entity to a member role model
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "member_id": entity.member_id,
            "role_id": entity.role_id,
            "created_by_id": entity.created_by_id,
            "updated_by_id": entity.updated_by_id,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> MemberRoleEntity:
        """
        convert a member role model to a member role entity
        """
        return MemberRoleEntity(
            id=row["id"],
            uuid=row["uuid"],
            member_id=row["member_id"],
            role_id=row["role_id"],
            created_by_id=row.get("created_by_id"),
            updated_by_id=row.get("updated_by_id"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
