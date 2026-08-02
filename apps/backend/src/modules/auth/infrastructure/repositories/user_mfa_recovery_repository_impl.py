from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.auth.domain.entities.user_mfa_recovery_entity import (
    UserMFARecoveryCodeEntity,
)
from src.modules.auth.domain.repositories.user_mfa_recovery_repository import (
    IUserMFARecoveryRepository,
)
from src.modules.auth.infrastructure.models.user_mfa_recovery_model import (
    UserMFARecoveryCodeModel,
)
from src.shared.infrastructure.repository.base_repository import BaseRepository


class UserMFARecoveryRepositoryImpl(
    BaseRepository[UserMFARecoveryCodeEntity], IUserMFARecoveryRepository
):
    """
    SQLAlchemy implementation of the IUserMFARecoveryRepository interface.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.table_name = UserMFARecoveryCodeModel.__tablename__

    def to_row(self, entity: UserMFARecoveryCodeEntity) -> dict:
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "mfa_id": entity.mfa_id,
            "hashed_recovery_code": entity.hashed_recovery_code,
            "is_revoked": entity.is_revoked,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> UserMFARecoveryCodeEntity:
        return UserMFARecoveryCodeEntity(
            id=row["id"],
            uuid=row["uuid"],
            mfa_id=row["mfa_id"],
            hashed_recovery_code=row["hashed_recovery_code"],
            is_revoked=row["is_revoked"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def add_many(
        self, entities: list[UserMFARecoveryCodeEntity]
    ) -> list[UserMFARecoveryCodeEntity]:
        rows = [self.to_row(entity) for entity in entities]
        return await self.bulk_create(rows)

    async def get_by_mfa_id(self, mfa_id: int) -> list[UserMFARecoveryCodeEntity]:
        return await self.filter(mfa_id=mfa_id, is_revoked=False)
