from src.shared.schemas import BaseSchema, DomainString


class StartSessionRequestSchema(BaseSchema):
    """
    Request schema for starting a visitor session (POST /visitors/sessions/start).
    ``ip_address`` and ``user_agent`` are derived server-side from the request,
    not accepted from the client.
    """

    organization_uuid: DomainString
    visitor_uuid: DomainString
    page: str | None = None
    referrer: str | None = None


class StartSessionResponseSchema(BaseSchema):
    """Response schema returned to the SDK after starting a session."""

    session_uuid: str
    visitor_uuid: str
    status: str
    visit_count: int


class PageEnterRequestSchema(BaseSchema):
    """Request schema for recording a page change."""

    session_uuid: DomainString
    url: str
    page_title: str | None = None


class HeartbeatRequestSchema(BaseSchema):
    """Request schema for a presence heartbeat."""

    session_uuid: DomainString


class EndSessionRequestSchema(BaseSchema):
    """Request schema for ending a session."""

    session_uuid: DomainString


class ActiveVisitorSchema(BaseSchema):
    """A single live visitor row for the agent dashboard."""

    visitor_uuid: str
    session_uuid: str
    status: str
    last_seen: str
    page: str | None = None
    name: str | None = None
    email: str | None = None
    phone: str | None = None


class ActiveVisitorsResponseSchema(BaseSchema):
    """Container for the active-visitors listing."""

    items: list[ActiveVisitorSchema]
    total: int


class UpdateSessionRequestSchema(BaseSchema):
    """Request schema for updating a visitor's identity mid-session."""

    visitor_uuid: DomainString
    name: str | None = None
    email: str | None = None
    phone: str | None = None


class VisitorSchema(BaseSchema):
    """Schema representing a website visitor stored in the database."""

    uuid: str
    external_id: str
    visit_count: int
    is_identified: bool
    last_seen_at: str  # ISO-8601 string
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    current_page: str | None = None
    device: str | None = None
    browser: str | None = None
    ip_address: str | None = None
    active_duration: int = 0


class VisitorsResponseSchema(BaseSchema):
    """Container for the visitors listing."""

    items: list[VisitorSchema]
    total: int


class VisitorsByCountryItemSchema(BaseSchema):
    """Schema representing visitor count and percentage for a single country."""

    country: str
    count: int
    percentage: float


class VisitorsByCountryResponseSchema(BaseSchema):
    """Schema representing the grouped visitors by country response."""

    total: int
    countries: list[VisitorsByCountryItemSchema]


class TopPagesItemSchema(BaseSchema):
    """Schema representing unique visitor count and percentage for a single page URL."""

    url: str
    count: int
    percentage: float


class TopPagesResponseSchema(BaseSchema):
    """Schema representing the top pages response."""

    total: int
    pages: list[TopPagesItemSchema]


class ActiveVisitorsCountResponseSchema(BaseSchema):
    """Schema representing the count of currently active visitors."""

    count: int


class AgentSubscriptionPayloadSchema(BaseSchema):
    """Schema for validating the agent's visitor subscription payload."""

    organization_uuid: str
