from src.modules.billing.domain.entities.billing_plan_limit_entity import (
    BillingPlanLimitEntity,
)
from src.modules.billing.domain.repositories.billing_plan_limit_repository import (
    IBillingPlanLimitRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    CreateError,
    DomainError,
)
from src.modules.billing.domain.events.billing_domain_events import (
    BillingPlanLimitCreatedEvent,
)


class BillingPlanLimitDomainService:
    """
    Service class for billing plan limit domain logic.
    """

    def __init__(self, repository: IBillingPlanLimitRepository):
        self.repository = repository

    async def create_billing_plan_limit(
        self,
        billing_plan_limit_entity: BillingPlanLimitEntity,
        actor_id: int,
    ) -> BillingPlanLimitEntity:
        """
        Creates a new billing plan limit with uniqueness check.
        """
        try:
            await self._ensure_feature_key_unique_for_plan(
                billing_plan_limit_entity.plan_id,
                billing_plan_limit_entity.feature_key,
            )

            created_billing_plan_limit = await self.repository.add(
                billing_plan_limit_entity
            )

            if not created_billing_plan_limit.id:
                raise CreateError(error="Failed to create billing plan limit")

            created_billing_plan_limit.add_event(
                BillingPlanLimitCreatedEvent(
                    plan_limit_id=created_billing_plan_limit.id,
                    plan_id=created_billing_plan_limit.plan_id,
                    feature_key=created_billing_plan_limit.feature_key,
                    actor_id=actor_id,
                )
            )
            return created_billing_plan_limit

        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to create billing plan limit",
                internal_details=str(e),
            ) from e

    async def get_billing_plan_limit_by_uuid(
        self, uuid: str
    ) -> BillingPlanLimitEntity | None:
        """
        Retrieves a billing plan limit by UUID.
        """
        return await self.repository.get_by(uuid=uuid)

    async def list_billing_plan_limit(
        self,
        plan_id: int,
    ) -> list[BillingPlanLimitEntity]:
        """
        Retrieves all billing plan limits for a specific plan.
        """
        return await self.repository.filter(plan_id=plan_id)

    async def _ensure_feature_key_unique_for_plan(
        self,
        plan_id: int,
        feature_key: str,
    ) -> None:
        """
        Ensure one plan does not have duplicate feature limits.
        """
        existing_limit = await self.repository.get_by(
            plan_id=plan_id,
            feature_key=feature_key,
        )

        if existing_limit:
            raise ConflictError(
                error="Billing plan limit with this feature key already exists for this plan"
            )

    async def get_plan_limit(
        self,
        plan_id: int,
        feature_key: str,
    ):
        """
        Get plan limit by plan id and feature key.
        """
        return await self.repository.get_by(
            plan_id=plan_id,
            feature_key=feature_key.strip().lower(),
        )
