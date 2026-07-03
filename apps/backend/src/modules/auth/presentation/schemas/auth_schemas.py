from datetime import datetime

from pydantic import Field

from src.shared.schemas import BaseSchema, DomainEmail, DomainString


class SignupRequestSchema(BaseSchema):
    """
    request schema to validate the payload
    """

    email: DomainEmail
    password: str = Field(..., description="Password of the user", min_length=8)
    captcha_token: str = Field(..., description="Captcha token from the frontend")


class LoginRequestSchema(BaseSchema):
    """
    request schema to validate the payload
    """

    email: DomainEmail
    password: DomainString
    captcha_token: str | None = Field(
        ..., description="Captcha token from the frontend"
    )


class OrganizationDetailsResponseSchema(BaseSchema):
    """
    response schema to validate the payload
    """

    uuid: str
    name: str
    slug: str
    logo: str | None
    status: str | None
    model_config = {"from_attributes": True, "extra": "ignore"}


class CountryDetailsResponseSchema(BaseSchema):
    """
    response schema for the user's country details
    """

    uuid: str
    name: str
    iso_code_2: str
    iso_code_3: str
    phone_code: str | None
    model_config = {"from_attributes": True, "extra": "ignore"}


class UserDetailsResponseSchema(BaseSchema):
    """
    response schema to validate the payload
    """

    uuid: str
    email: DomainEmail
    username: str | None
    full_name: str | None
    avatar: str | None
    email_verified_at: datetime | None
    is_online: bool = True
    avatar_bg: str | None
    is_onboarded: bool
    phone_number: str | None
    country: CountryDetailsResponseSchema | None = None
    # last_organization_uuid: str | None
    # organization: OrganizationDetailsResponseSchema

    model_config = {"from_attributes": True, "extra": "ignore"}


class SignupResponseSchema(BaseSchema):
    """
    response schema to validate the payload
    """

    uuid: str
    email: DomainEmail

    model_config = {"from_attributes": True}


class EditProfileRequestSchema(BaseSchema):
    """
    request schema to validate the payload
    """

    full_name: str | None = Field(default=None, description="The full name of the user")
    avatar: str | None = Field(default=None, description="The avatar URL of the user")
    phone_number: str | None = Field(
        default=None, description="The phone number of the user"
    )
    country_uuid: str | None = Field(
        default=None, description="The UUID of the user's country"
    )
