from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.billing.domain.entities.billing_subscription_entity import (
    BillingSubscriptionEntity,
)
from src.modules.billing.domain.repositories.billing_subscription_repository import (
    IBillingSubscriptionRepository,
)
from src.modules.billing.infrastructure.models.billing_subscription_model import (
    BillingSubscriptionModel,
)
from src.shared.infrastructure.repository.organization_repository import (
    OrganizationRepository,
)


class BillingSubscriptionRepositoryImpl(
    OrganizationRepository[BillingSubscriptionEntity],
    IBillingSubscriptionRepository,
):
    """
    SQLAlchemy implementation of the billing subscription repository.
    """

    def __init__(self, session: AsyncSession, organization_id: int):
        """
        Initialize BillingSubscriptionRepositoryImpl with async database session
        and organization id.
        """
        self.session = session
        self.organization_id = organization_id
        self.table_name = BillingSubscriptionModel.__tablename__

        super().__init__(
            session=session,
            table_name=self.table_name,
            organization_id=organization_id,
        )

    def to_row(self, entity: BillingSubscriptionEntity) -> dict:
        """
        Convert billing subscription entity to database row.
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "organization_id": entity.organization_id,
            "plan_id": entity.plan_id,
            "status": entity.status,
            "auto_renew": entity.auto_renew,
            "cancel_at_period_end": entity.cancel_at_period_end,
            "start_date": entity.start_date,
            "cancelled_at": entity.cancelled_at,
            "current_period_start": entity.current_period_start,
            "current_period_end": entity.current_period_end,
            "billing_cycle": entity.billing_cycle,
            "trial_ends_at": entity.trial_ends_at,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> BillingSubscriptionEntity:
        """
        Convert database row to billing subscription entity.
        """
        return BillingSubscriptionEntity(
            id=row["id"],
            uuid=row["uuid"],
            organization_id=row["organization_id"],
            plan_id=row["plan_id"],
            status=row["status"],
            auto_renew=row["auto_renew"],
            cancel_at_period_end=row["cancel_at_period_end"],
            start_date=row["start_date"],
            cancelled_at=row["cancelled_at"],
            current_period_start=row["current_period_start"],
            current_period_end=row["current_period_end"],
            billing_cycle=row["billing_cycle"],
            trial_ends_at=row["trial_ends_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
