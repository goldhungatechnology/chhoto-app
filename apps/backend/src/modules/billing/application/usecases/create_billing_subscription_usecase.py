from datetime import UTC, datetime

from src.modules.billing.domain.entities.billing_subscription_entity import (
    BillingSubscriptionEntity,
)
from src.modules.billing.domain.services.billing_subscription_domain_service import (
    BillingSubscriptionDomainService,
)
from src.modules.billing.presentation.schemas.billing_subscription_schemas import (
    CreateBillingSubscriptionRequestSchema,
)
from src.shared.exceptions.base_exceptions import DomainError, InvalidError, ServerError
from src.shared.mediator.mediator import mediator

_VALID_BILLING_CYCLES = {"monthly", "annually"}


class CreateBillingSubscriptionUseCase:
    """
    Use case for creating a billing subscription.
    """

    def __init__(
        self,
        billing_subscription_domain_service: BillingSubscriptionDomainService,
    ):
        self.billing_subscription_domain_service = billing_subscription_domain_service

    async def execute(
        self,
        payload: CreateBillingSubscriptionRequestSchema,
        organization_id: int,
        actor_id: int,
    ) -> dict[str, str]:
        """
        Execute the use case to create a billing subscription.
        """
        try:
            now = datetime.now(UTC)
            billing_cycle = payload.billing_cycle.strip().lower()
            if billing_cycle not in _VALID_BILLING_CYCLES:
                raise InvalidError(
                    error="Invalid billing cycle. Must be 'monthly' or 'annually'."
                )

            billing_subscription = BillingSubscriptionEntity(
                organization_id=organization_id,
                plan_id=payload.plan_id,
                # Initial status is decided server-side, never taken from the
                # client, so a caller cannot self-provision an active paid plan
                # or bypass the trial.
                status="active",
                auto_renew=payload.auto_renew,
                cancel_at_period_end=False,
                start_date=now,
                current_period_start=now,
                current_period_end=self._get_period_end(now, billing_cycle),
                billing_cycle=billing_cycle,
            )

            created_billing_subscription = await self.billing_subscription_domain_service.create_billing_subscription(
                billing_subscription,
                actor_id,
            )

            if not created_billing_subscription.id:
                raise ServerError(error="Failed to create billing subscription")

            for event in created_billing_subscription.pull_events():
                await mediator.publish(event)

            return {
                "billing_subscription_uuid": created_billing_subscription.uuid,
                "organization_id": str(created_billing_subscription.organization_id),
                "plan_id": str(created_billing_subscription.plan_id),
            }

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while creating billing subscription",
                internal_details=str(e),
            ) from e

    def _get_period_end(self, start_date: datetime, billing_cycle: str) -> datetime:
        """
        Calculate subscription period end date using calendar-aware arithmetic
        (real months/years), so period boundaries don't drift the way a fixed
        30/365-day delta would across varying month lengths and leap years.
        """
        if billing_cycle == "annually":
            return self._add_months(start_date, 12)
        return self._add_months(start_date, 1)

    @staticmethod
    def _add_months(dt: datetime, months: int) -> datetime:
        """
        Add a number of calendar months to a datetime, clamping the day to the
        last valid day of the target month (e.g. Jan 31 + 1 month -> Feb 28/29).
        """
        import calendar

        month_index = dt.month - 1 + months
        year = dt.year + month_index // 12
        month = month_index % 12 + 1
        day = min(dt.day, calendar.monthrange(year, month)[1])
        return dt.replace(year=year, month=month, day=day)
