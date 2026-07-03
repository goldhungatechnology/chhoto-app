from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.auth.domain.entities.user_onboarding_entity import UserOnboardingEntity
from src.modules.auth.domain.repositories.user_onboarding_repository import (
    IUserOnboardingRepository,
)
from src.modules.auth.infrastructure.models.user_onboarding_model import (
    UserOnboardingModel,
)
from src.shared.infrastructure.repository.base_repository import BaseRepository


class UserOnboardingRepositoryImpl(
    BaseRepository[UserOnboardingEntity], IUserOnboardingRepository
):
    """
    sqlalchemy implementation of the user onboarding repository interface
    """

    def __init__(self, session: AsyncSession):
        """Initialize UserOnboardingRepositoryImpl with an async database session."""
        self.session = session
        self.table_name = UserOnboardingModel.__tablename__

    def to_row(self, entity: UserOnboardingEntity) -> dict:
        """
        convert a user onboarding entity to a user onboarding model
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "user_id": entity.user_id,
            "theme": entity.theme,
            "referral_source": entity.referral_source,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> UserOnboardingEntity:
        """
        convert a user onboarding model to a user onboarding entity
        """
        return UserOnboardingEntity(
            id=row["id"],
            uuid=row["uuid"],
            user_id=row["user_id"],
            theme=row["theme"],
            referral_source=row.get("referral_source"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
