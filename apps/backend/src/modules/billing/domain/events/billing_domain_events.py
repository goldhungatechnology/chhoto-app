from dataclasses import dataclass
from src.shared.domain.events.base_domain_events import DomainEvent


@dataclass(kw_only=True, frozen=True)
class BillingPlanCreatedEvent(DomainEvent):
    """
    Event triggered when billing plan is created.
    """

    plan_id: int
    plan_slug: str
    actor_id: int | None = None


@dataclass(kw_only=True, frozen=True)
class BillingPlanLimitCreatedEvent(DomainEvent):
    """
    Event triggered when a billing plan limit is created.
    """

    plan_limit_id: int
    plan_id: int
    feature_key: str
    actor_id: int | None = None


@dataclass(kw_only=True, frozen=True)
class BillingSubscriptionCreatedEvent(DomainEvent):
    """
    Event is triggered when a billing subscription is created.
    """

    subscription_id: int
    organization_id: int
    plan_id: int
    actor_id: int | None = None


@dataclass(kw_only=True, frozen=True)
class BillingSubscriptionCancelledEvent(DomainEvent):
    """
    Event triggered when a billing subscription is cancelled.
    """

    subscription_id: int
    organization_id: int
    plan_id: int
    actor_id: int | None = None


@dataclass(kw_only=True, frozen=True)
class OrganizationFeatureUsageCreatedEvent(DomainEvent):
    """
    Event triggered when organization feature usage is created.
    """

    feature_usage_id: int
    organization_id: int
    subscription_id: int
    feature_key: str
    actor_id: int | None = None
