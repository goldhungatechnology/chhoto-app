from src.modules.motivation.domain.enums.motivation_enums import (
    QuotesStatusEnum,
    QuotesTextStyleEnum,
)
from src.shared.schemas import BaseSchema, DomainString


class UpdateDailyMotivationConfigRequestSchema(BaseSchema):
    """
    Request schema for updating daily motivation config.
    """

    sys_quote_source: bool | None = None
    is_enabled: bool | None = None
    allow_reactions: bool | None = None
    display_time: str | None = None
    font_style: QuotesTextStyleEnum | None = None


class DailyMotivationConfigResponseSchema(BaseSchema):
    """
    Response schema for daily motivation config.
    """

    uuid: str
    sys_quote_source: bool | None = None
    is_enabled: bool | None = None
    allow_reactions: bool | None = None
    display_time: str | None = None
    font_style: str | None = None

    model_config = {"from_attributes": True, "extra": "ignore"}


class CreateMotivationQuoteRequestSchema(BaseSchema):
    """
    Request schema for creating a custom motivation quote.
    """

    context: DomainString
    author_name: DomainString | None = None
    font_style: QuotesTextStyleEnum
    status: QuotesStatusEnum | None
    theme_color: DomainString
    bg_image: DomainString | None = None


class UpdateMotivationQuoteRequestSchema(BaseSchema):
    """
    Request schema for updating a custom motivation quote.
    """

    context: DomainString | None = None
    author_name: DomainString | None = None
    status: QuotesStatusEnum | None = None
    font_style: QuotesTextStyleEnum | None = None
    status: QuotesStatusEnum | None = None
    theme_color: DomainString | None = None
    bg_image: DomainString | None = None


class MotivationQuoteResponseSchema(BaseSchema):
    """
    Response schema for motivation quote.
    """

    uuid: str
    context: str
    author_name: str | None = None
    status: str
    is_sys_default: bool
    font_style: str
    theme_color: str
    bg_image: str | None = None

    model_config = {"from_attributes": True, "extra": "ignore"}


class MotivationQuoteListResponseSchema(BaseSchema):
    """
    Response schema for motivation quote list.
    """

    items: list[MotivationQuoteResponseSchema]
    total: int


class ReactToMotivationQuoteRequestSchema(BaseSchema):
    """
    Request schema for reacting to a motivation quote.
    """

    quote_uuid: str
    reaction_type: DomainString


class MotivationQuoteReactionResponseSchema(BaseSchema):
    """
    Response schema for motivation quote reaction.
    """

    uuid: str
    member_id: int
    quote_id: int
    reaction_type: str

    model_config = {"from_attributes": True, "extra": "ignore"}


class AddMotivationColorRequestSchema(BaseSchema):
    """
    Request schema for adding motivation color.
    """

    color_code: DomainString


class MotivationColorResponseSchema(BaseSchema):
    """
    Response schema for motivation color.
    """

    uuid: str
    config_id: int
    color_code: str

    model_config = {"from_attributes": True, "extra": "ignore"}


class MotivationColorListResponseSchema(BaseSchema):
    """
    Response schema for motivation color list.
    """

    items: list[MotivationColorResponseSchema]
