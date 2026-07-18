from datetime import datetime

from pydantic import Field, HttpUrl

from src.shared.schemas import BaseSchema


class CreateLinkRequestSchema(BaseSchema):
    """
    Request schema to create a new short link.
    """

    destination_url: HttpUrl = Field(
        ..., description="The destination URL the short link redirects to"
    )
    custom_slug: str | None = Field(
        default=None,
        description="Custom short URL slug. Auto-generated if not provided.",
        max_length=255,
    )
    title: str | None = Field(
        default=None, description="Optional title for the link", max_length=255
    )
    tags: list[str] | None = Field(
        default=None, description="Array of tags for categorizing the link"
    )
    auto_expire: datetime | None = Field(
        default=None,
        description="When the link automatically expires. Null means never.",
    )


class LinkResponseSchema(BaseSchema):
    """
    Response schema for a single link.
    """

    uuid: str
    destination_url: str
    short_url: str
    title: str | None
    tags: list[str] | None
    auto_expire: datetime | None
    total_clicks: int
    created_at: datetime

    model_config = {"from_attributes": True, "extra": "ignore"}
