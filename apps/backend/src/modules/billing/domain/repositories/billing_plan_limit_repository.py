from src.modules.billing.domain.entities.billing_plan_limit_entity import (
    BillingPlanLimitEntity,
)

from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IBillingPlanLimitRepository(IBaseRepository[BillingPlanLimitEntity]):
    """
    Interface for billing plan limit repository.
    """
