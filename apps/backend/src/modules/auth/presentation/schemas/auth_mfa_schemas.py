from pydantic import Field

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
    """

    temp_token: DomainString = Field(
        ...,
        description="The temporary token received from the login endpoint.",
    )
    otp_code: DomainString = Field(
        ...,
        min_length=6,
        max_length=6,
        description="The 6-digit TOTP code from the authenticator app.",
    )
