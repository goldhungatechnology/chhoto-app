from typing import Literal

from src.shared.schemas import BaseSchema


class InterfaceSetupRequestSchema(BaseSchema):
    theme: Literal["light", "dark"]
    language: str
