from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity


@dataclass(kw_only=True)
class BillingPlanEntity(BaseEntity):
    """
    Entity representing a billing plan.
    """

    name: str = field(
        metadata={
            "description": "The display name of the billing plan, for example Free plan, Pro plan, or Enterprise plan"
        }
    )
    slug: str = field(
        metadata={
            "description": "The unique slug of the billing plan, for example free, pro, or enterprise",
            "unique": True,
            "index": True,
        }
    )
    price: float = field(metadata={"description": "The price of the billing plan"})
    currency: str = field(
        metadata={
            "description": "The currency used for the plan price, for example EUR or USD or NPR"
        }
    )
    interval: str = field(
        metadata={
            "description": "The billing interval of the plan, for example monthly or annually"
        }
    )
    is_active: bool = field(
        default=True,
        metadata={
            "description": "Whether the billing plan is active and available for subscription"
        },
    )

    def activate(self):
        """
        Activate the billing plan.
        """
        self.is_active = True
        self.mark_updated()

    def deactivate(self):
        """
        Deactivate the billing plan.
        """
        self.is_active = False
        self.mark_updated()
