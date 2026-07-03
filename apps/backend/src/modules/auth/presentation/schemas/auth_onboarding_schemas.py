from typing import Literal

from src.shared.schemas import BaseSchema, DomainString


class OnboardingRequestSchema(BaseSchema):
    """
    request schema to validate the payload
    """

    theme: Literal["light", "dark"]
    referral_source: DomainString

