from src.modules.billing.domain.entities.organization_feature_usage_entity import (
    OrganizationFeatureUsageEntity,
)
from src.shared.domain.repository.organization_repository_interface import (
    IOrganizationRepository,
)


class IOrganizationFeatureUsageRepository(
    IOrganizationRepository[OrganizationFeatureUsageEntity]
):
    """
    Interface for organization feature usage repository.
    """

    async def get_usage(
        self,
        subscription_id: int,
        feature_key: str,
    ) -> OrganizationFeatureUsageEntity | None:
        """
        Get usage by subscription id and feature key.
        """
        raise NotImplementedError

    async def increment_usage(
        self,
        subscription_id: int,
        feature_key: str,
        amount: int,
    ) -> OrganizationFeatureUsageEntity:
        """
        Increment usage value by amount.
        """
        raise NotImplementedError

    async def reset_usage(
        self,
        subscription_id: int,
    ) -> list[OrganizationFeatureUsageEntity]:
        """
        Reset all usage values for a subscription.
        """
        raise NotImplementedError
