from src.modules.billing.domain.entities.billing_subscription_entity import (
    BillingSubscriptionEntity,
)
from src.shared.domain.repository.organization_repository_interface import (
    IOrganizationRepository,
)


class IBillingSubscriptionRepository(
    IOrganizationRepository[BillingSubscriptionEntity]
):
    """
    Interface for billing subscription repository.
    """
