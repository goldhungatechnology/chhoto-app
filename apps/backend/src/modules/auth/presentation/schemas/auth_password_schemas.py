from pydantic import Field, ValidationInfo, field_validator

from src.shared.schemas.base_schema import BaseSchema, DomainEmail, DomainString


class PasswordResetRequestSchema(BaseSchema):
    """
    Schema for password reset request.
    """

    old_password: DomainString
    new_password: DomainString = Field(min_length=8)
    keep_current_session: bool = True

    @field_validator("new_password")
    @classmethod
    def validate_passwords(
        cls,
        new_password: str,
        info: ValidationInfo,
    ) -> str:
        """
        validates the new password is different from the old password.
        """
        old_password = info.data.get("old_password")

        if old_password == new_password:
            raise ValueError("New password must be different from old password.")

        return new_password


class PasswordForgotRequestSchema(BaseSchema):
    """
    Schema for password forgot request.
    """

    email: DomainEmail


class PasswordForgotVerifyRequestSchema(BaseSchema):
    """
    Schema for password forgot verification request.

    The emailed reset token is the only credential required; the old password
    is intentionally NOT requested, since the user has forgotten it.
    """

    token: DomainString
    new_password: DomainString = Field(min_length=8)
