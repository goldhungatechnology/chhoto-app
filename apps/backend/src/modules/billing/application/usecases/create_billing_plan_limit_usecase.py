from src.modules.billing.domain.entities.billing_plan_limit_entity import (
    BillingPlanLimitEntity,
)
from src.modules.billing.domain.services.billing_plan_limit_domain_service import (
    BillingPlanLimitDomainService,
)
from src.modules.billing.presentation.schemas.billing_plan_limit_schemas import (
    CreateBillingPlanLimitRequestSchema,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError
from src.shared.mediator.mediator import mediator


class CreateBillingPlanLimitUseCase:
    """
    Use case for creating a billing plan limit.
    """

    def __init__(
        self,
        billing_plan_limit_domain_service: BillingPlanLimitDomainService,
    ):
        self.billing_plan_limit_domain_service = billing_plan_limit_domain_service

    async def execute(
        self,
        payload: CreateBillingPlanLimitRequestSchema,
        actor_id: int,
    ) -> dict[str, str]:
        """
        Execute the use case to create a billing plan limit.
        """
        try:
            billing_plan_limit = BillingPlanLimitEntity(
                plan_id=payload.plan_id,
                feature_key=payload.feature_key.strip().lower(),
                limit_value=payload.limit_value,
                is_unlimited=payload.is_unlimited,
            )

            created_billing_plan_limit = (
                await self.billing_plan_limit_domain_service.create_billing_plan_limit(
                    billing_plan_limit,
                    actor_id,
                )
            )

            if not created_billing_plan_limit.id:
                raise ServerError(error="Failed to create billing plan limit")

            for event in created_billing_plan_limit.pull_events():
                await mediator.publish(event)

            return {
                "billing_plan_limit_uuid": created_billing_plan_limit.uuid,
                "feature_key": created_billing_plan_limit.feature_key,
            }

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while creating billing plan limit",
                internal_details=str(e),
            ) from e
