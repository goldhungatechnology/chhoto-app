from src.modules.billing.domain.entities.organization_feature_usage_entity import (
    OrganizationFeatureUsageEntity,
)
from src.modules.billing.domain.repositories.organization_feature_usage_repository import (
    IOrganizationFeatureUsageRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    CreateError,
    DomainError,
)

from src.modules.billing.domain.events.billing_domain_events import (
    OrganizationFeatureUsageCreatedEvent,
)


class OrganizationFeatureUsageDomainService:
    """
    Service class for organization feature usage domain logic.
    """

    def __init__(self, repository: IOrganizationFeatureUsageRepository):
        self.repository = repository

    async def create_organization_feature_usage(
        self,
        organization_feature_usage_entity: OrganizationFeatureUsageEntity,
        actor_id: int,
    ) -> OrganizationFeatureUsageEntity:
        """
        Create organization feature usage with duplicate check.
        """
        try:
            await self._ensure_feature_usage_unique(
                subscription_id=organization_feature_usage_entity.subscription_id,
                feature_key=organization_feature_usage_entity.feature_key,
            )

            created_feature_usage = await self.repository.add(
                organization_feature_usage_entity
            )

            if not created_feature_usage.id:
                raise CreateError(error="Failed to create organization feature usage")

            created_feature_usage.add_event(
                OrganizationFeatureUsageCreatedEvent(
                    feature_usage_id=created_feature_usage.id,
                    organization_id=created_feature_usage.organization_id,
                    subscription_id=created_feature_usage.subscription_id,
                    feature_key=created_feature_usage.feature_key,
                    actor_id=actor_id,
                )
            )

            return created_feature_usage

        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to create organization feature usage",
                internal_details=str(e),
            ) from e

    async def list_organization_feature_usage(
        self,
        subscription_id: int,
    ) -> list[OrganizationFeatureUsageEntity]:
        """
        List all feature usage records for a subscription.
        """
        return await self.repository.filter(subscription_id=subscription_id)

    async def get_usage(
        self,
        subscription_id: int,
        feature_key: str,
    ) -> OrganizationFeatureUsageEntity | None:
        """
        Get usage for a specific subscription and feature key.
        """
        return await self.repository.get_usage(
            subscription_id=subscription_id,
            feature_key=feature_key,
        )

    async def increment_usage(
        self,
        subscription_id: int,
        feature_key: str,
        amount: int,
    ) -> OrganizationFeatureUsageEntity:
        """
        Increment usage value for a specific feature.
        """
        try:
            return await self.repository.increment_usage(
                subscription_id=subscription_id,
                feature_key=feature_key,
                amount=amount,
            )
        except ValueError as e:
            raise CreateError(error=str(e)) from e

    async def reset_usage(
        self,
        subscription_id: int,
    ) -> list[OrganizationFeatureUsageEntity]:
        """
        Reset all feature usages for a subscription.
        """
        return await self.repository.reset_usage(subscription_id=subscription_id)

    async def _ensure_feature_usage_unique(
        self,
        subscription_id: int,
        feature_key: str,
    ) -> None:
        """
        Ensure same feature usage is not created twice for same subscription.
        """
        existing_feature_usage = await self.repository.get_by(
            subscription_id=subscription_id,
            feature_key=feature_key.strip().lower(),
        )

        if existing_feature_usage:
            raise ConflictError(
                error="Feature usage already exists for this subscription"
            )
