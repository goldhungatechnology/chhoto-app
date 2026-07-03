from src.modules.billing.domain.entities.billing_plan_entity import BillingPlanEntity
from src.shared.domain.repository.base_repository_interface import IBaseRepository


class IBillingPlanRepository(IBaseRepository[BillingPlanEntity]):
    """
    Interface for billing plan repository.
    """
