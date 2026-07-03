from pydantic import Field

from src.core.config.settings import config
from src.shared.schemas.base_schema import BaseSchema, DomainString


class EmailVerificationRequestSchema(BaseSchema):
    """
    Schema for email verification request.
    """

    token: DomainString = Field(
        ...,
        description="The token sent to the user's email for verification.",
        max_length=config.TOKEN_DIGIT,
        min_length=config.TOKEN_DIGIT,
    )
