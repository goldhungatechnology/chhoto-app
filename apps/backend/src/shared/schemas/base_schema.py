from typing import Annotated
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field as Field,
    StringConstraints,
    field_validator as field_validator,
    model_validator as model_validator,
    computed_field as computed_field,
)

DomainString = Annotated[str, StringConstraints(max_length=255)]
DomainEmail = Annotated[EmailStr, StringConstraints(max_length=255)]


class BaseSchema(BaseModel):
    """
    Base schema for all pydantic models
    """

    model_config = ConfigDict(
        extra="forbid",
        json_encoders={datetime: lambda v: v.isoformat().replace("+00:00", "Z")},
    )
