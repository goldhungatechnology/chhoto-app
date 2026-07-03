from src.modules.billing.domain.entities.billing_subscription_entity import (
    BillingSubscriptionEntity,
)
from src.modules.billing.domain.events.billing_domain_events import (
    BillingSubscriptionCreatedEvent,
)
from src.modules.billing.domain.repositories.billing_subscription_repository import (
    IBillingSubscriptionRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    CreateError,
    DomainError,
)


class BillingSubscriptionDomainService:
    """
    Service class for billing subscription domain logic.
    """

    def __init__(self, repository: IBillingSubscriptionRepository):
        self.repository = repository

    async def create_billing_subscription(
        self,
        billing_subscription_entity: BillingSubscriptionEntity,
        actor_id: int,
    ) -> BillingSubscriptionEntity:
        """
        Creates a billing subscription with organization subscription check.
        """
        try:
            await self._ensure_organization_has_no_active_subscription()

            created_billing_subscription = await self.repository.add(
                billing_subscription_entity
            )

            if not created_billing_subscription.id:
                raise CreateError(error="Failed to create billing subscription")

            created_billing_subscription.add_event(
                BillingSubscriptionCreatedEvent(
                    subscription_id=created_billing_subscription.id,
                    organization_id=created_billing_subscription.organization_id,
                    plan_id=created_billing_subscription.plan_id,
                    actor_id=actor_id,
                )
            )

            return created_billing_subscription

        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to create billing subscription",
                internal_details=str(e),
            ) from e

    async def get_billing_subscription_by_uuid(
        self, uuid: str
    ) -> BillingSubscriptionEntity | None:
        """
        Retrieves a billing subscription by UUID.
        """
        return await self.repository.get_by(uuid=uuid)

    async def get_active_billing_subscription(
        self,
    ) -> BillingSubscriptionEntity | None:
        """
        Retrieves the current entitling subscription for the organization.

        Both ``active`` and ``trialing`` subscriptions grant entitlements, so a
        trialing organization must be returned here too — otherwise entitlement
        checks and usage increments would wrongly treat trialing orgs as having
        no subscription at all.
        """
        return await self.repository.get_by(status__in=["active", "trialing"])

    async def _ensure_organization_has_no_active_subscription(self) -> None:
        """
        Ensure organization does not already have active or trialing subscription.
        """
        active_subscription = await self.repository.get_by(status="active")

        if active_subscription:
            raise ConflictError(
                error="Organization already has an active billing subscription"
            )

        trialing_subscription = await self.repository.get_by(status="trialing")

        if trialing_subscription:
            raise ConflictError(
                error="Organization already has a trialing billing subscription"
            )
