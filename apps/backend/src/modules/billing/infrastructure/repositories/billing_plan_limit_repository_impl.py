from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.billing.domain.entities.billing_plan_limit_entity import (
    BillingPlanLimitEntity,
)
from src.modules.billing.domain.repositories.billing_plan_limit_repository import (
    IBillingPlanLimitRepository,
)
from src.modules.billing.infrastructure.models.billing_plan_limit_model import (
    BillingPlanLimitModel,
)
from src.shared.infrastructure.repository.base_repository import BaseRepository


class BillingPlanLimitRepositoryImpl(
    BaseRepository[BillingPlanLimitEntity],
    IBillingPlanLimitRepository,
):
    """
    SQLAlchemy implementation of the billing plan limit repository.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize BillingPlanLimitRepositoryImpl with async database session.
        """
        self.session = session
        self.table_name = BillingPlanLimitModel.__tablename__

        super().__init__(
            session=session,
            table_name=self.table_name,
        )

    def to_row(self, entity: BillingPlanLimitEntity) -> dict:
        """
        Convert billing plan limit entity to database row.
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "plan_id": entity.plan_id,
            "feature_key": entity.feature_key,
            "limit_value": entity.limit_value,
            "is_unlimited": entity.is_unlimited,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> BillingPlanLimitEntity:
        """
        Convert database row to billing plan limit entity.
        """
        return BillingPlanLimitEntity(
            id=row["id"],
            uuid=row["uuid"],
            plan_id=row["plan_id"],
            feature_key=row["feature_key"],
            limit_value=row["limit_value"],
            is_unlimited=row["is_unlimited"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
