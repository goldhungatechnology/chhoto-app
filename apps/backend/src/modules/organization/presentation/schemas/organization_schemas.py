from datetime import datetime
from typing import Any

import validators

from src.modules.organization.presentation.schemas.organization_media_schemas import (
    OrganizationMediaResponseSchema,
)
from src.shared.schemas import BaseSchema, DomainString, field_validator


class CreateOrganizationOnboardingRequestSchema(BaseSchema):
    """
    Request schema for creating organization onboarding.
    """

    size_range: DomainString
    use_case: list[DomainString]
    industry: DomainString
    previous_tool: DomainString | None = None


class CreateOrganizationRequestSchema(BaseSchema):
    """
    Request schema for creating organization.
    """

    name: DomainString
    description: DomainString | None = None
    logo: DomainString | None = None
    domain: DomainString
    onboarding: CreateOrganizationOnboardingRequestSchema

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, value: str):
        """
        Validate the domain using the validators library.
        """
        if not validators.domain(value):
            raise ValueError("Invalid domain")

        return value.lower()


class CurrentOrganizationDetailsResponseSchema(BaseSchema):
    """
    Response schema for organization details.
    """

    uuid: str
    name: str
    slug: str
    logo: str | None
    domain: str
    media: OrganizationMediaResponseSchema | None = None
    description: str | None = None

    model_config = {"from_attributes": True, "extra": "ignore"}


class EditOrganizationRequestSchema(BaseSchema):
    """
    Request schema for editing organization.
    """

    name: DomainString | None = None
    description: DomainString | None = None
    logo: DomainString | None = None
    domain: DomainString | None = None
    whatsapp: DomainString | None = None
    linkedin: DomainString | None = None
    email: DomainString | None = None
    phone_number: DomainString | None = None
    messenger: DomainString | None = None
    instagram: DomainString | None = None
    twitter: DomainString | None = None
    telegram: DomainString | None = None

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, value: str):
        """
        Validate the domain using the validators library.
        """
        if not validators.domain(value):
            raise ValueError("Invalid domain")

        return value.lower()

    @field_validator(
        "whatsapp",
        "linkedin",
        "email",
        "phone_number",
        "messenger",
        "instagram",
        "twitter",
        "telegram",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value: Any) -> Any:
        """
        Converts empty strings into None.
        """
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class OrganizationMemberUserSchema(BaseSchema):
    """
    User details embedded in an organization-member listing response.
    """

    uuid: str
    email: str
    avatar_bg: str
    full_name: str | None
    avatar: str | None
    is_online: bool = False

    model_config = {
        "from_attributes": True,
    }


class OrganizationMemberResponseSchema(BaseSchema):
    """
    Schema for a single organization member row.
    """

    uuid: str
    status: str
    joined_at: datetime
    role: str | None = None
    user: OrganizationMemberUserSchema | None = None


class OrganizationMemberListResponseSchema(BaseSchema):
    """
    Paginated container for organization-member listings, mirroring the
    audit-events listing shape (items + total + limit + offset).
    """

    items: list[OrganizationMemberResponseSchema]
    total: int
    limit: int
    offset: int
