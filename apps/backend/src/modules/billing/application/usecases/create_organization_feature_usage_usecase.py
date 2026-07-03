from src.modules.billing.domain.entities.organization_feature_usage_entity import (
    OrganizationFeatureUsageEntity,
)
from src.modules.billing.domain.services.organization_feature_usage_domain_service import (
    OrganizationFeatureUsageDomainService,
)
from src.modules.billing.presentation.schemas.organization_feature_usage_schemas import (
    CreateOrganizationFeatureUsageRequestSchema,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError
from src.shared.mediator.mediator import mediator


class CreateOrganizationFeatureUsageUseCase:
    """
    Use case for creating organization feature usage.
    """

    def __init__(
        self,
        organization_feature_usage_domain_service: OrganizationFeatureUsageDomainService,
    ):
        self.organization_feature_usage_domain_service = (
            organization_feature_usage_domain_service
        )

    async def execute(
        self,
        payload: CreateOrganizationFeatureUsageRequestSchema,
        organization_id: int,
        actor_id: int,
    ) -> dict[str, str | int]:
        """
        Execute the use case to create organization feature usage.
        """
        try:
            organization_feature_usage = OrganizationFeatureUsageEntity(
                organization_id=organization_id,
                subscription_id=payload.subscription_id,
                feature_key=payload.feature_key.strip().lower(),
                used_value=payload.used_value,
            )

            created_feature_usage = await self.organization_feature_usage_domain_service.create_organization_feature_usage(
                organization_feature_usage,
                actor_id,
            )

            if not created_feature_usage.id:
                raise ServerError(error="Failed to create organization feature usage")

            for event in created_feature_usage.pull_events():
                await mediator.publish(event)

            return {
                "organization_feature_usage_uuid": created_feature_usage.uuid,
                "feature_key": created_feature_usage.feature_key,
                "used_value": created_feature_usage.used_value,
            }

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while creating organization feature usage",
                internal_details=str(e),
            ) from e
