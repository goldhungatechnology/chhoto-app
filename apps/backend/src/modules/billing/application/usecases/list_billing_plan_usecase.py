from src.modules.billing.domain.services.billing_plan_domain_service import (
    BillingPlanDomainService,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError


class ListBillingPlanUseCase:
    """
    Use case for listing billing plans.
    """

    def __init__(
        self,
        billing_plan_domain_service: BillingPlanDomainService,
    ):
        self.billing_plan_domain_service = billing_plan_domain_service

    async def execute(self) -> list[dict]:
        """
        Execute the use case to list all billing plans.
        """
        try:
            billing_plan = await self.billing_plan_domain_service.list_billing_plan()

            return [
                {
                    "uuid": billing_plan.uuid,
                    "name": billing_plan.name,
                    "slug": billing_plan.slug,
                    "price": billing_plan.price,
                    "currency": billing_plan.currency,
                    "interval": billing_plan.interval,
                    "is_active": billing_plan.is_active,
                }
                for billing_plan in billing_plan
            ]

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while listing billing plans",
                internal_details=str(e),
            ) from e
