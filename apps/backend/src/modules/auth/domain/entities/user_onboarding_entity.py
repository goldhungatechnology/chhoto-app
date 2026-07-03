from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin


@dataclass(kw_only=True)
class UserOnboardingEntity(BaseEntity, AuditMixin):
    """
    Entity representing a user onboarding in the system.
    """

    user_id: int = field(
        metadata={
            "description": "The ID of the user associated with this onboarding",
            "index": True,
            "on_delete": "cascade",
        }
    )

    theme: str = field(
        metadata={
            "description": "The theme selected by the user during onboarding (e.g., 'light', 'dark')"
        }
    )
    referral_source: str | None = field(
        default=None,
        metadata={
            "description": "The referral source selected by the user during onboarding (e.g., 'social media', 'friend referral')"
        },
    )
