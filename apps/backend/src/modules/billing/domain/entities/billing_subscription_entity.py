from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.shared.domain.entity.base_entity import BaseEntity


@dataclass(kw_only=True)
class BillingSubscriptionEntity(BaseEntity):
    """
    Entity representing an organization's billing subscription.
    """

    organization_id: int = field(
        metadata={
            "description": "The organization id this subscription belongs to",
            "index": True,
            "on_delete": "cascade",
        }
    )
    plan_id: int = field(
        metadata={
            "description": "The billing plan id selected for this subscription",
            "index": True,
            "on_delete": "restrict",
        }
    )

    status: str = field(
        metadata={
            "description": "The subscription status, for example trialing, active, past_due, cancelled, or expired"
        }
    )

    auto_renew: bool = field(
        default=True,
        metadata={"description": "Whether the subscription should renew automatically"},
    )

    cancel_at_period_end: bool = field(
        default=False,
        metadata={
            "description": "Whether the subscription should be cancelled at the end of current billing period"
        },
    )
    start_date: datetime | None = field(
        default=None,
        metadata={"description": "The datetime when the subscription started"},
    )
    cancelled_at: datetime | None = field(
        default=None,
        metadata={"description": "The datetime when the subscription was cancelled"},
    )
    current_period_start: datetime | None = field(
        default=None,
        metadata={"description": "The start datetime of the current billing period"},
    )
    current_period_end: datetime | None = field(
        default=None,
        metadata={"description": "The end datetime of the current billing period"},
    )
    billing_cycle: str = field(
        metadata={
            "description": "The billing cycle of the subscription, for example monthly or annually"
        }
    )
    trial_ends_at: datetime | None = field(
        default=None,
        metadata={"description": "The datetime when the trial period ends"},
    )

    def activate(self):
        """
        Activate the subscription.
        """
        self.status = "active"
        self.mark_updated()

    def mark_past_due(self):
        """
        Mark the subscription as past due.
        """
        self.status = "past_due"
        self.mark_updated()

    def cancel(self):
        """
        Cancel the subscription.
        """
        self.status = "cancelled"
        self.cancelled_at = datetime.now(UTC)
        self.mark_updated()

    def expire(self):
        """
        Expire the subscription.
        """
        self.status = "expired"
        self.mark_updated()

    def is_active(self) -> bool:
        """
        Check whether subscription is active and not expired by period date.
        """
        if self.status.lower() != "active":
            return False

        if self.current_period_end and self.current_period_end < datetime.now(UTC):
            return False

        return True

    def is_trialing(self) -> bool:
        """
        Check whether subscription is currently in trial period.
        """
        if self.status.lower() != "trialing":
            return False

        if self.trial_ends_at and self.trial_ends_at >= datetime.now(UTC):
            return True

        return False

    def mark_cancel_at_period_end(self):
        """
        Mark subscription to cancel at the end of current billing period.
        """
        self.cancel_at_period_end = True
        self.auto_renew = False
        self.mark_updated()
