from src.modules.billing.domain.entities.billing_plan_entity import BillingPlanEntity
from src.modules.billing.domain.services.billing_plan_domain_service import (
    BillingPlanDomainService,
)
from src.modules.billing.presentation.schemas.billing_plan_schemas import (
    CreateBillingPlanRequestSchema,
)
from src.shared.exceptions.base_exceptions import DomainError, ServerError
from src.shared.mediator.mediator import mediator


class CreateBillingPlanUseCase:
    """
    Use case for creating a billing plan.
    """

    def __init__(
        self,
        billing_plan_domain_service: BillingPlanDomainService,
    ):
        self.billing_plan_domain_service = billing_plan_domain_service

    async def execute(
        self,
        payload: CreateBillingPlanRequestSchema,
        actor_id: int,
    ) -> dict[str, str]:
        """
        Execute the use case to create a billing plan.
        """
        try:
            billing_plan = BillingPlanEntity(
                name=payload.name,
                slug=self._get_slug_from_name(payload.name),
                price=payload.price,
                currency=payload.currency.upper(),
                interval=payload.interval.lower(),
                is_active=payload.is_active,
            )

            created_billing_plan = (
                await self.billing_plan_domain_service.create_billing_plan(
                    billing_plan, actor_id
                )
            )

            if not created_billing_plan.id:
                raise ServerError(error="Failed to create billing plan")

            for event in created_billing_plan.pull_events():
                await mediator.publish(event)

            return {
                "billing_plan_uuid": created_billing_plan.uuid,
                "billing_plan_slug": created_billing_plan.slug,
            }

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while creating billing plan",
                internal_details=str(e),
            ) from e

    def _get_slug_from_name(self, name: str) -> str:
        """
        Generate a slug from the billing plan name.
        """
        return name.strip().lower().replace(" ", "-")
