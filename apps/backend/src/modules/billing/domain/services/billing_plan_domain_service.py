from src.modules.billing.domain.entities.billing_plan_entity import BillingPlanEntity
from src.modules.billing.domain.repositories.billing_plan_repository import (
    IBillingPlanRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    CreateError,
    DomainError,
)

from src.modules.billing.domain.events.billing_domain_events import (
    BillingPlanCreatedEvent,
)


class BillingPlanDomainService:
    """
    Service class for billing plan domain logic.
    """

    def __init__(self, repository: IBillingPlanRepository):
        self.repository = repository

    async def create_billing_plan(
        self, billing_plan_entity: BillingPlanEntity, actor_id: int
    ) -> BillingPlanEntity:
        """
        Creates a new billing plan with uniqueness checks.
        """
        try:
            await self._ensure_slug_unique(billing_plan_entity.slug)

            created_billing_plan = await self.repository.add(billing_plan_entity)

            if not created_billing_plan.id:
                raise CreateError(error="Failed to create billing plan")

            created_billing_plan.add_event(
                BillingPlanCreatedEvent(
                    plan_id=created_billing_plan.id,
                    plan_slug=created_billing_plan.slug,
                    actor_id=actor_id,
                )
            )

            return created_billing_plan

        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to create billing plan",
                internal_details=str(e),
            ) from e

    async def get_billing_plan_by_uuid(self, uuid: str) -> BillingPlanEntity | None:
        """
        Retrieves a billing plan by its UUID.
        """
        return await self.repository.get_by(uuid=uuid)

    async def get_billing_plan_by_slug(self, slug: str) -> BillingPlanEntity | None:
        """
        Retrieves a billing plan by its slug.
        """
        return await self.repository.get_by(slug=slug)

    async def list_billing_plan(self) -> list[BillingPlanEntity]:
        """
        List only active billing plans.
        """
        return await self.repository.filter(is_active=True)

    async def _ensure_slug_unique(self, slug: str) -> None:
        """
        Ensure billing plan slug is unique.
        """
        existing_plan = await self.repository.get_by(slug=slug)

        if existing_plan:
            raise ConflictError(error="Billing plan with this slug already exists")
