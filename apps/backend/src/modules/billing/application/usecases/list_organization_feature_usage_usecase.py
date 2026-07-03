from src.modules.billing.domain.services.organization_feature_usage_domain_service import (
    OrganizationFeatureUsageDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class ListOrganizationFeatureUsageUseCase:
    """
    Use case for listing organization feature usages.
    """

    def __init__(
        self,
        organization_feature_usage_domain_service: OrganizationFeatureUsageDomainService,
    ):
        self.organization_feature_usage_domain_service = (
            organization_feature_usage_domain_service
        )

    async def execute(self, subscription_id: int) -> list[dict]:
        """
        Execute the use case to list feature usages by subscription id.
        """
        try:
            feature_usages = await self.organization_feature_usage_domain_service.list_organization_feature_usage(
                subscription_id=subscription_id
            )

            return [
                {
                    "uuid": feature_usage.uuid,
                    "organization_id": feature_usage.organization_id,
                    "subscription_id": feature_usage.subscription_id,
                    "feature_key": feature_usage.feature_key,
                    "used_value": feature_usage.used_value,
                }
                for feature_usage in feature_usages
            ]

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while listing organization feature usage",
                internal_details=str(e),
            ) from e
