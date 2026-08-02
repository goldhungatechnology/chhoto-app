from pydantic import Field, model_validator

from src.shared.schemas.base_schema import BaseSchema, DomainString


class SetupMFAResponseSchema(BaseSchema):
    """
    Schema for MFA setup response.
    """

    secret: str = Field(
        ...,
        description="The TOTP secret key for provisioning the authenticator app.",
    )
    auth_url: str = Field(
        ...,
        description="The otpauth:// URL for QR code generation.",
    )


class ConfirmMFARequestSchema(BaseSchema):
    """
    Schema for confirming (enabling) MFA request.
    """

    otp_code: DomainString = Field(
        ...,
        min_length=6,
        max_length=6,
        description="The 6-digit TOTP code from the authenticator app.",
    )


class ConfirmMFAResponseSchema(BaseSchema):
    """
    Schema for confirming (enabling) MFA response.
    """

    verified: bool = True
    recovery_codes: list[str] = Field(
        ...,
        description="The generated emergency recovery codes for MFA.",
    )


class DisableMFARequestSchema(BaseSchema):
    """
    Schema for disabling MFA request.
    """

    password: DomainString = Field(
        ...,
        description="The user's current password for confirmation.",
    )


class VerifyMFARequestSchema(BaseSchema):
    """
    Schema for verifying MFA during login request.

    Either the 6-digit TOTP code from the authenticator app OR a single-use
    recovery code must be provided (never both).
    """

    temp_token: DomainString = Field(
        ...,
        description="The temporary token received from the login endpoint.",
    )
    otp_code: DomainString | None = Field(
        default=None,
        min_length=6,
        max_length=6,
        description="The 6-digit TOTP code from the authenticator app.",
    )
    recovery_code: DomainString | None = Field(
        default=None,
        min_length=9,
        max_length=9,
        description="A single-use recovery code in XXXX-XXXX format.",
    )

    @model_validator(mode="after")
    def validate_single_code_provided(self) -> "VerifyMFARequestSchema":
        """
        Ensures exactly one of otp_code or recovery_code is provided.
        """
        if self.otp_code and self.recovery_code:
            raise ValueError("Provide either otp_code or recovery_code, not both.")
        if not self.otp_code and not self.recovery_code:
            raise ValueError("Provide either otp_code or recovery_code.")
        return self
