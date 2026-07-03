from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.billing.domain.entities.organization_feature_usage_entity import (
    OrganizationFeatureUsageEntity,
)
from src.modules.billing.domain.repositories.organization_feature_usage_repository import (
    IOrganizationFeatureUsageRepository,
)
from src.modules.billing.infrastructure.models.organization_feature_usage_model import (
    OrganizationFeatureUsageModel,
)
from src.shared.infrastructure.repository.organization_repository import (
    OrganizationRepository,
)


class OrganizationFeatureUsageRepositoryImpl(
    OrganizationRepository[OrganizationFeatureUsageEntity],
    IOrganizationFeatureUsageRepository,
):
    """
    SQLAlchemy implementation of the organization feature usage repository.
    """

    def __init__(self, session: AsyncSession, organization_id: int):
        """
        Initialize repository with async database session and organization id.
        """
        self.session = session
        self.organization_id = organization_id
        self.table_name = OrganizationFeatureUsageModel.__tablename__

        super().__init__(
            session=session,
            table_name=self.table_name,
            organization_id=organization_id,
        )

    def to_row(self, entity: OrganizationFeatureUsageEntity) -> dict:
        """
        Convert organization feature usage entity to database row.
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "organization_id": entity.organization_id,
            "subscription_id": entity.subscription_id,
            "feature_key": entity.feature_key,
            "used_value": entity.used_value,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> OrganizationFeatureUsageEntity:
        """
        Convert database row to organization feature usage entity.
        """
        return OrganizationFeatureUsageEntity(
            id=row["id"],
            uuid=row["uuid"],
            organization_id=row["organization_id"],
            subscription_id=row["subscription_id"],
            feature_key=row["feature_key"],
            used_value=row["used_value"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def get_usage(
        self,
        subscription_id: int,
        feature_key: str,
    ) -> OrganizationFeatureUsageEntity | None:
        """
        Get usage by subscription id and feature key.
        """
        return await self.get_by(
            subscription_id=subscription_id,
            feature_key=feature_key.strip().lower(),
        )

    async def increment_usage(
        self,
        subscription_id: int,
        feature_key: str,
        amount: int,
    ) -> OrganizationFeatureUsageEntity:
        """
        Atomically increment usage value by amount.

        Performed as a single ``used_value = used_value + :amount`` UPDATE so
        concurrent increments cannot lose each other's writes (the previous
        read-modify-write was subject to a lost-update race).
        """
        if amount < 0:
            raise ValueError("Increment amount must be non-negative")

        sql = text(
            f"""
            UPDATE {self.table_name}
            SET used_value = used_value + :amount, updated_at = NOW()
            WHERE subscription_id = :subscription_id
              AND feature_key = :feature_key
              AND {self._org_filter_sql()}
            RETURNING *
            """
        )
        result = await self.session.execute(
            sql,
            {
                "amount": amount,
                "subscription_id": subscription_id,
                "feature_key": feature_key.strip().lower(),
                **self._org_params(),
            },
        )
        row = result.mappings().one_or_none()
        if row is None:
            raise ValueError("Feature usage not found")
        return self.to_entity(dict(row))

    async def reset_usage(
        self,
        subscription_id: int,
    ) -> list[OrganizationFeatureUsageEntity]:
        """
        Reset all usage values for a subscription.
        """
        feature_usages = await self.filter(subscription_id=subscription_id)

        reset_feature_usages = []

        for feature_usage in feature_usages:
            feature_usage.update_used_value(0)
            updated_feature_usage = await self.update(feature_usage)
            reset_feature_usages.append(updated_feature_usage)

        return reset_feature_usages
