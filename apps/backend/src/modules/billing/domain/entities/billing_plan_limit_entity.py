from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.exceptions.base_exceptions import InvalidError


@dataclass(kw_only=True)
class BillingPlanLimitEntity(BaseEntity):
    """
    Entity representing billing plan limits.
    """

    plan_id: int = field(
        metadata={
            "description": "The billing plan id this limit belongs to",
            "index": True,
            "on_delete": "cascade",
        }
    )
    feature_key: str = field(
        metadata={
            "description": "The feature key this limit applies to, for example max_users, max_uploads, or storage"
        }
    )
    limit_value: int | None = field(
        default=None,
        metadata={
            "description": "The numeric limit value for the feature. It can be None if the feature is unlimited"
        },
    )
    is_unlimited: bool = field(
        default=False,
        metadata={"description": "Whether this feature is unlimited for the plan"},
    )

    def make_unlimited(self):
        """
        Mark this plan limit as unlimited.
        """
        self.is_unlimited = True
        self.limit_value = None
        self.mark_updated()

    def set_limit(self, limit_value: int):
        """
        Set a fixed limit for this feature.
        """
        if limit_value < 0:
            raise InvalidError(error="Plan limit_value cannot be negative")
        self.is_unlimited = False
        self.limit_value = limit_value
        self.mark_updated()

    def __post_init__(self):
        """
        Ensure a plan limit is either unlimited or has a fixed limit, not both.
        """
        if self.is_unlimited and self.limit_value is not None:
            raise InvalidError(error="Unlimited plan limit cannot have limit_value")
