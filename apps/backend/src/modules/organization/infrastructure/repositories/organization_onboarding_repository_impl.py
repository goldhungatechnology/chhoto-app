from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.organization.domain.entities.organization_onboarding_entity import (
    OrganizationOnboardingEntity,
)
from src.modules.organization.domain.repositories.organization_onboarding_repository import (
    IOrganizationOnboardingRepository,
)
from src.modules.organization.infrastructure.models.organization_onboarding_model import (
    OrganizationOnboardingModel,
)
from src.shared.infrastructure.repository.base_repository import BaseRepository


class OrganizationOnboardingRepositoryImpl(
    BaseRepository[OrganizationOnboardingEntity], IOrganizationOnboardingRepository
):
    """
    SQLAlchemy implementation of the organization repository
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.table_name = OrganizationOnboardingModel.__tablename__
        super().__init__(session, self.table_name)

    def to_row(self, entity: OrganizationOnboardingEntity) -> dict:
        """
        Convert an OrganizationOnboardingEntity to a dictionary representing a database row.
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "organization_id": entity.organization_id,
            "size_range": entity.size_range,
            "use_case": entity.use_case,
            "industry": entity.industry,
            "previous_tool": entity.previous_tool,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> OrganizationOnboardingEntity:
        """
        Convert a database row dictionary to an OrganizationOnboardingEntity.
        """
        return OrganizationOnboardingEntity(
            id=row["id"],
            uuid=row["uuid"],
            organization_id=row["organization_id"],
            size_range=row.get("size_range"),
            use_case=row.get("use_case"),
            industry=row.get("industry"),
            previous_tool=row.get("previous_tool"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
