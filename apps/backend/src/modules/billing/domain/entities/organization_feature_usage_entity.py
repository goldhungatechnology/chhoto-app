from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.exceptions.base_exceptions import InvalidError


@dataclass(kw_only=True)
class OrganizationFeatureUsageEntity(BaseEntity):
    """
    Entity representing feature usage of an organization subscription.
    """

    organization_id: int = field(
        metadata={
            "description": "The organization id this feature usage belongs to",
            "index": True,
            "on_delete": "cascade",
        }
    )

    subscription_id: int = field(
        metadata={
            "description": "The subscription id this feature usage belongs to",
            "index": True,
            "on_delete": "cascade",
        }
    )

    feature_key: str = field(
        metadata={
            "description": "The feature key being tracked",
            "example": "max_users",
        }
    )

    used_value: int = field(
        metadata={
            "description": "The used value for this feature",
            "example": "5",
        }
    )

    def update_used_value(self, used_value: int):
        """
        Update used value of the feature.
        """
        if used_value < 0:
            raise InvalidError(error="Feature used_value cannot be negative")
        self.used_value = used_value
        self.mark_updated()
