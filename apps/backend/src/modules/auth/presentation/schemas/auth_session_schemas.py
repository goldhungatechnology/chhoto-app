from datetime import datetime, UTC
from src.shared.schemas import BaseSchema, computed_field


class RevokeAllSessionsRequestSchema(BaseSchema):
    """
    validate payload
    """

    keep_current_session: bool = True


class RevokeSessionRequestSchema(BaseSchema):
    """
    validate payload for revoking a single session
    """

    session_uuid: str


class CurrentSessionResponseSchema(BaseSchema):
    """
    response schema for current session details
    """

    uuid: str
    device: str | None = None
    browser: str | None = None
    ip_address: str | None = None
    city: str | None = None
    country: str | None = None
    country_code: str | None = None
    created_at: datetime | None = None
    organization_uuid: str | None = None

    expires_at: datetime | None = None
    revoked_at: datetime | None = None

    model_config = {
        "from_attributes": True,
    }

    @computed_field
    @property
    def status(self) -> str:
        """
        compute the status of the session based on revoked_at and expires_at
        """
        if self.revoked_at is not None:
            return "revoked"
        if self.expires_at is not None and self.expires_at < datetime.now(UTC):
            return "expired"
        return "active"
