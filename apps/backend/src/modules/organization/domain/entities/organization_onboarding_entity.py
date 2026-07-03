from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity


@dataclass(kw_only=True)
class OrganizationOnboardingEntity(BaseEntity):
    """
    Entity representing the onboarding status of an organization.
    """

    organization_id: int = field(
        metadata={
            "index": True,
            "on_delete": "cascade",
            "description": "The ID of the organization associated with this onboarding record",
        }
    )

    size_range: str | None = field(
        default=None,
        metadata={
            "description": "The size range of the organization (e.g., '1-10', '11-50', '51-200', etc.)"
        },
    )

    use_case: list[str] | None = field(
        default=None,
        metadata={
            "description": "The primary use cases or reasons for the organization's interest in the product"
        },
    )

    industry: str | None = field(
        default=None,
        metadata={
            "description": "The industry or sector the organization operates in (e.g., 'Technology', 'Healthcare', 'Finance', etc.)"
        },
    )

    previous_tool: str | None = field(
        default=None,
        metadata={
            "description": "The tool the organization was previously using, if any (can be skipped)"
        },
    )
