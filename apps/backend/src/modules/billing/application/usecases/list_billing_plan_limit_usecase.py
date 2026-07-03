from src.modules.billing.domain.services.billing_plan_limit_domain_service import (
    BillingPlanLimitDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class ListBillingPlanLimitUseCase:
    """
    Use Case for listing billing plan limit.
    """

    def __init__(
        self, billing_plan_limit_domain_service: BillingPlanLimitDomainService
    ):
        self.billing_plan_limit_domain_service = billing_plan_limit_domain_service

    async def execute(self, plan_id: int) -> list[dict]:
        """
        Execute the usecase to list all the billing plan limit.
        """
        try:
            billing_plan_limit = (
                await self.billing_plan_limit_domain_service.list_billing_plan_limit(
                    plan_id=plan_id
                )
            )
            return [
                {
                    "uuid": billing_plan_limit.uuid,
                    "plan_id": billing_plan_limit.plan_id,
                    "feature_key": billing_plan_limit.feature_key,
                    "limit_value": billing_plan_limit.limit_value,
                    "is_unlimited": billing_plan_limit.is_unlimited,
                }
                for billing_plan_limit in billing_plan_limit
            ]

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while listing billing plan limit",
                internal_details=str(e),
            ) from e
