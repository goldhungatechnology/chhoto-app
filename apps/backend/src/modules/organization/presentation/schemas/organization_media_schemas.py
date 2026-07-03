from src.shared.schemas import BaseSchema


class OrganizationMediaResponseSchema(BaseSchema):
    """
    Response schema for organization media.
    """

    whatsapp: str | None
    linkedin: str | None
    email: str | None
    phone_number: str | None
    messenger: str | None
    instagram: str | None
    twitter: str | None
    telegram: str | None

    model_config = {"from_attributes": True, "extra": "ignore"}
